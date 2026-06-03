from __future__ import annotations

import torch

from src.ukan_course.models import AttentionUKAN, UKAN, UNet


def test_ukan_forward_shape_no_kan() -> None:
    model = UKAN(num_classes=1, input_channels=3, embed_dims=[32, 48, 64], no_kan=True)
    x = torch.randn(1, 3, 64, 64)
    y = model(x)
    assert y.shape == (1, 1, 64, 64)


def test_attention_ukan_forward_shape_no_kan() -> None:
    model = AttentionUKAN(num_classes=1, input_channels=3, embed_dims=[32, 48, 64], no_kan=True)
    x = torch.randn(1, 3, 64, 64)
    y = model(x)
    assert y.shape == (1, 1, 64, 64)


def test_unet_forward_shape() -> None:
    model = UNet(num_classes=1, input_channels=3, base_channels=8)
    x = torch.randn(1, 3, 64, 64)
    y = model(x)
    assert y.shape == (1, 1, 64, 64)
