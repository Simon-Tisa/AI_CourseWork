from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from .kan import KANLinear


def to_2tuple(value: int | tuple[int, int]) -> tuple[int, int]:
    if isinstance(value, tuple):
        return value
    return (value, value)


class DropPath(nn.Module):
    def __init__(self, drop_prob: float = 0.0) -> None:
        super().__init__()
        self.drop_prob = drop_prob

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.drop_prob == 0.0 or not self.training:
            return x
        keep_prob = 1 - self.drop_prob
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
        random_tensor.floor_()
        return x.div(keep_prob) * random_tensor


def init_module_weights(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.trunc_normal_(module.weight, std=0.02)
        if module.bias is not None:
            nn.init.constant_(module.bias, 0)
    elif isinstance(module, nn.LayerNorm):
        nn.init.constant_(module.bias, 0)
        nn.init.constant_(module.weight, 1.0)
    elif isinstance(module, nn.Conv2d):
        fan_out = module.kernel_size[0] * module.kernel_size[1] * module.out_channels
        fan_out //= module.groups
        module.weight.data.normal_(0, math.sqrt(2.0 / fan_out))
        if module.bias is not None:
            module.bias.data.zero_()


class KANLayer(nn.Module):
    def __init__(
        self,
        in_features: int,
        hidden_features: int | None = None,
        out_features: int | None = None,
        drop: float = 0.0,
        no_kan: bool = False,
    ) -> None:
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.dim = in_features

        kan_kwargs = {
            "grid_size": 5,
            "spline_order": 3,
            "scale_noise": 0.1,
            "scale_base": 1.0,
            "scale_spline": 1.0,
            "base_activation": torch.nn.SiLU,
            "grid_eps": 0.02,
            "grid_range": [-1, 1],
        }

        linear_cls = nn.Linear if no_kan else KANLinear
        if no_kan:
            self.fc1 = linear_cls(in_features, hidden_features)
            self.fc2 = linear_cls(hidden_features, out_features)
            self.fc3 = linear_cls(hidden_features, out_features)
        else:
            self.fc1 = linear_cls(in_features, hidden_features, **kan_kwargs)
            self.fc2 = linear_cls(hidden_features, out_features, **kan_kwargs)
            self.fc3 = linear_cls(hidden_features, out_features, **kan_kwargs)

        self.dwconv_1 = DWBNReLU(hidden_features)
        self.dwconv_2 = DWBNReLU(hidden_features)
        self.dwconv_3 = DWBNReLU(hidden_features)
        self.drop = nn.Dropout(drop)
        self.apply(init_module_weights)

    def forward(self, x: torch.Tensor, height: int, width: int) -> torch.Tensor:
        batch, num_tokens, channels = x.shape

        x = self.fc1(x.reshape(batch * num_tokens, channels))
        x = x.reshape(batch, num_tokens, channels).contiguous()
        x = self.dwconv_1(x, height, width)
        x = self.fc2(x.reshape(batch * num_tokens, channels))
        x = x.reshape(batch, num_tokens, channels).contiguous()
        x = self.dwconv_2(x, height, width)
        x = self.fc3(x.reshape(batch * num_tokens, channels))
        x = x.reshape(batch, num_tokens, channels).contiguous()
        x = self.dwconv_3(x, height, width)
        return x


class KANBlock(nn.Module):
    def __init__(
        self,
        dim: int,
        drop: float = 0.0,
        drop_path: float = 0.0,
        norm_layer=nn.LayerNorm,
        no_kan: bool = False,
    ) -> None:
        super().__init__()
        self.drop_path = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()
        self.norm2 = norm_layer(dim)
        self.layer = KANLayer(
            in_features=dim,
            hidden_features=dim,
            drop=drop,
            no_kan=no_kan,
        )
        self.apply(init_module_weights)

    def forward(self, x: torch.Tensor, height: int, width: int) -> torch.Tensor:
        return x + self.drop_path(self.layer(self.norm2(x), height, width))


class DWConv(nn.Module):
    def __init__(self, dim: int = 768) -> None:
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, 3, 1, 1, bias=True, groups=dim)

    def forward(self, x: torch.Tensor, height: int, width: int) -> torch.Tensor:
        batch, _, channels = x.shape
        x = x.transpose(1, 2).view(batch, channels, height, width)
        x = self.dwconv(x)
        return x.flatten(2).transpose(1, 2)


class DWBNReLU(nn.Module):
    def __init__(self, dim: int = 768) -> None:
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, 3, 1, 1, bias=True, groups=dim)
        self.bn = nn.BatchNorm2d(dim)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor, height: int, width: int) -> torch.Tensor:
        batch, _, channels = x.shape
        x = x.transpose(1, 2).view(batch, channels, height, width)
        x = self.dwconv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x.flatten(2).transpose(1, 2)


class PatchEmbed(nn.Module):
    def __init__(
        self,
        img_size: int | tuple[int, int] = 224,
        patch_size: int | tuple[int, int] = 7,
        stride: int = 4,
        in_chans: int = 3,
        embed_dim: int = 768,
    ) -> None:
        super().__init__()
        img_size = to_2tuple(img_size)
        patch_size = to_2tuple(patch_size)
        self.img_size = img_size
        self.patch_size = patch_size
        self.height = img_size[0] // patch_size[0]
        self.width = img_size[1] // patch_size[1]
        self.num_patches = self.height * self.width
        self.proj = nn.Conv2d(
            in_chans,
            embed_dim,
            kernel_size=patch_size,
            stride=stride,
            padding=(patch_size[0] // 2, patch_size[1] // 2),
        )
        self.norm = nn.LayerNorm(embed_dim)
        self.apply(init_module_weights)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, int, int]:
        x = self.proj(x)
        _, _, height, width = x.shape
        x = x.flatten(2).transpose(1, 2)
        x = self.norm(x)
        return x, height, width


class ConvLayer(nn.Module):
    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class DecoderConvLayer(nn.Module):
    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, in_ch, 3, padding=1),
            nn.BatchNorm2d(in_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class UKAN(nn.Module):
    def __init__(
        self,
        num_classes: int,
        input_channels: int = 3,
        deep_supervision: bool = False,
        embed_dims: list[int] | tuple[int, int, int] = (128, 160, 256),
        no_kan: bool = False,
        img_size: int = 224,
        drop_rate: float = 0.0,
        drop_path_rate: float = 0.0,
        norm_layer=nn.LayerNorm,
        depths: list[int] | tuple[int, int, int] = (1, 1, 1),
    ) -> None:
        super().__init__()
        del deep_supervision
        embed_dims = list(embed_dims)
        kan_input_dim = embed_dims[0]

        self.encoder1 = ConvLayer(input_channels, kan_input_dim // 8)
        self.encoder2 = ConvLayer(kan_input_dim // 8, kan_input_dim // 4)
        self.encoder3 = ConvLayer(kan_input_dim // 4, kan_input_dim)

        self.norm3 = norm_layer(embed_dims[1])
        self.norm4 = norm_layer(embed_dims[2])
        self.dnorm3 = norm_layer(embed_dims[1])
        self.dnorm4 = norm_layer(embed_dims[0])

        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, sum(depths))]
        self.block1 = nn.ModuleList(
            [
                KANBlock(
                    dim=embed_dims[1],
                    drop=drop_rate,
                    drop_path=dpr[0],
                    norm_layer=norm_layer,
                    no_kan=no_kan,
                )
            ]
        )
        self.block2 = nn.ModuleList(
            [
                KANBlock(
                    dim=embed_dims[2],
                    drop=drop_rate,
                    drop_path=dpr[1],
                    norm_layer=norm_layer,
                    no_kan=no_kan,
                )
            ]
        )
        self.dblock1 = nn.ModuleList(
            [
                KANBlock(
                    dim=embed_dims[1],
                    drop=drop_rate,
                    drop_path=dpr[0],
                    norm_layer=norm_layer,
                    no_kan=no_kan,
                )
            ]
        )
        self.dblock2 = nn.ModuleList(
            [
                KANBlock(
                    dim=embed_dims[0],
                    drop=drop_rate,
                    drop_path=dpr[1],
                    norm_layer=norm_layer,
                    no_kan=no_kan,
                )
            ]
        )

        self.patch_embed3 = PatchEmbed(
            img_size=img_size // 4,
            patch_size=3,
            stride=2,
            in_chans=embed_dims[0],
            embed_dim=embed_dims[1],
        )
        self.patch_embed4 = PatchEmbed(
            img_size=img_size // 8,
            patch_size=3,
            stride=2,
            in_chans=embed_dims[1],
            embed_dim=embed_dims[2],
        )

        self.decoder1 = DecoderConvLayer(embed_dims[2], embed_dims[1])
        self.decoder2 = DecoderConvLayer(embed_dims[1], embed_dims[0])
        self.decoder3 = DecoderConvLayer(embed_dims[0], embed_dims[0] // 4)
        self.decoder4 = DecoderConvLayer(embed_dims[0] // 4, embed_dims[0] // 8)
        self.decoder5 = DecoderConvLayer(embed_dims[0] // 8, embed_dims[0] // 8)

        self.skip_attention4 = nn.Identity()
        self.skip_attention3 = nn.Identity()
        self.skip_attention2 = nn.Identity()
        self.skip_attention1 = nn.Identity()

        self.final = nn.Conv2d(embed_dims[0] // 8, num_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch = x.shape[0]

        out = F.relu(F.max_pool2d(self.encoder1(x), 2, 2))
        skip1 = out
        out = F.relu(F.max_pool2d(self.encoder2(out), 2, 2))
        skip2 = out
        out = F.relu(F.max_pool2d(self.encoder3(out), 2, 2))
        skip3 = out

        out, height, width = self.patch_embed3(out)
        for block in self.block1:
            out = block(out, height, width)
        out = self.norm3(out)
        out = out.reshape(batch, height, width, -1).permute(0, 3, 1, 2).contiguous()
        skip4 = out

        out, height, width = self.patch_embed4(out)
        for block in self.block2:
            out = block(out, height, width)
        out = self.norm4(out)
        out = out.reshape(batch, height, width, -1).permute(0, 3, 1, 2).contiguous()

        out = F.relu(F.interpolate(self.decoder1(out), scale_factor=(2, 2), mode="bilinear"))
        out = self.skip_attention4(torch.add(out, skip4))
        _, _, height, width = out.shape
        out = out.flatten(2).transpose(1, 2)
        for block in self.dblock1:
            out = block(out, height, width)

        out = self.dnorm3(out)
        out = out.reshape(batch, height, width, -1).permute(0, 3, 1, 2).contiguous()
        out = F.relu(F.interpolate(self.decoder2(out), scale_factor=(2, 2), mode="bilinear"))
        out = self.skip_attention3(torch.add(out, skip3))
        _, _, height, width = out.shape
        out = out.flatten(2).transpose(1, 2)

        for block in self.dblock2:
            out = block(out, height, width)

        out = self.dnorm4(out)
        out = out.reshape(batch, height, width, -1).permute(0, 3, 1, 2).contiguous()

        out = F.relu(F.interpolate(self.decoder3(out), scale_factor=(2, 2), mode="bilinear"))
        out = self.skip_attention2(torch.add(out, skip2))
        out = F.relu(F.interpolate(self.decoder4(out), scale_factor=(2, 2), mode="bilinear"))
        out = self.skip_attention1(torch.add(out, skip1))
        out = F.relu(F.interpolate(self.decoder5(out), scale_factor=(2, 2), mode="bilinear"))

        return self.final(out)
