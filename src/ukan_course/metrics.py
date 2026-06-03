from __future__ import annotations

import torch


def _binary_prediction(logits: torch.Tensor, threshold: float = 0.5) -> torch.Tensor:
    return (torch.sigmoid(logits) >= threshold).to(torch.bool)


def _binary_target(target: torch.Tensor) -> torch.Tensor:
    return (target >= 0.5).to(torch.bool)


def _safe_divide(numerator: float, denominator: float, empty_score: float = 1.0) -> float:
    if denominator == 0:
        return empty_score
    return float(numerator / denominator)


def iou_score(logits: torch.Tensor, target: torch.Tensor) -> float:
    pred = _binary_prediction(logits)
    truth = _binary_target(target)
    intersection = torch.logical_and(pred, truth).sum().item()
    union = torch.logical_or(pred, truth).sum().item()
    return _safe_divide(intersection, union)


def dice_score(logits: torch.Tensor, target: torch.Tensor) -> float:
    pred = _binary_prediction(logits)
    truth = _binary_target(target)
    intersection = torch.logical_and(pred, truth).sum().item()
    total = pred.sum().item() + truth.sum().item()
    return _safe_divide(2 * intersection, total)


def binary_stats(logits: torch.Tensor, target: torch.Tensor) -> dict[str, int]:
    pred = _binary_prediction(logits)
    truth = _binary_target(target)
    return {
        "tp": int(torch.logical_and(pred, truth).sum().item()),
        "fp": int(torch.logical_and(pred, torch.logical_not(truth)).sum().item()),
        "fn": int(torch.logical_and(torch.logical_not(pred), truth).sum().item()),
        "tn": int(torch.logical_and(torch.logical_not(pred), torch.logical_not(truth)).sum().item()),
    }


def scores_from_stats(stats: dict[str, int]) -> dict[str, float]:
    tp = stats["tp"]
    fp = stats["fp"]
    fn = stats["fn"]
    tn = stats["tn"]
    return {
        "iou": _safe_divide(tp, tp + fp + fn),
        "dice": _safe_divide(2 * tp, 2 * tp + fp + fn),
        "precision": _safe_divide(tp, tp + fp),
        "recall": _safe_divide(tp, tp + fn),
        "specificity": _safe_divide(tn, tn + fp),
    }
