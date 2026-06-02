from __future__ import annotations

from .attention import ChannelSpatialAttention
from .ukan import UKAN


class AttentionUKAN(UKAN):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        embed_dims = list(kwargs.get("embed_dims", (128, 160, 256)))
        self.skip_attention4 = ChannelSpatialAttention(embed_dims[1])
        self.skip_attention3 = ChannelSpatialAttention(embed_dims[0])
        self.skip_attention2 = ChannelSpatialAttention(embed_dims[0] // 4)
        self.skip_attention1 = ChannelSpatialAttention(embed_dims[0] // 8)
