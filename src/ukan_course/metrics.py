from __future__ import annotations

import torch


def _binary_prediction(logits: torch.Tensor, threshold: float = 0.5) -> torch.Tensor:
    return (torch.sigmoid(logits) >= threshold).to(torch.bool)


def _binary_target(target: torch.Tensor) -> torch.Tensor:
    return (target >= 0.5).to(torch.bool)


def iou_score(logits: torch.Tensor, target: torch.Tensor, smooth: float = 1e-7) -> float:
    pred = _binary_prediction(logits)
    truth = _binary_target(target)
    intersection = torch.logical_and(pred, truth).sum().item()
    union = torch.logical_or(pred, truth).sum().item()
    return float((intersection + smooth) / (union + smooth))


def dice_score(logits: torch.Tensor, target: torch.Tensor, smooth: float = 1e-7) -> float:
    pred = _binary_prediction(logits)
    truth = _binary_target(target)
    intersection = torch.logical_and(pred, truth).sum().item()
    total = pred.sum().item() + truth.sum().item()
    return float((2 * intersection + smooth) / (total + smooth))
