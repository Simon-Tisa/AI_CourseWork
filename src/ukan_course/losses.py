from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class BCEDiceLoss(nn.Module):
    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        bce = F.binary_cross_entropy_with_logits(logits, target)
        probs = torch.sigmoid(logits)
        batch_size = target.size(0)
        probs = probs.view(batch_size, -1)
        target = target.view(batch_size, -1)
        intersection = (probs * target).sum(dim=1)
        dice = (2.0 * intersection + 1e-5) / (probs.sum(dim=1) + target.sum(dim=1) + 1e-5)
        dice_loss = 1.0 - dice.mean()
        return 0.5 * bce + dice_loss
