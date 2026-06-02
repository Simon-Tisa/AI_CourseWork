from __future__ import annotations

import torch

from src.ukan_course.metrics import dice_score, iou_score


def test_iou_score_perfect_prediction() -> None:
    logits = torch.tensor([[[[10.0, -10.0], [10.0, -10.0]]]])
    target = torch.tensor([[[[1.0, 0.0], [1.0, 0.0]]]])
    assert iou_score(logits, target) == 1.0


def test_dice_score_perfect_prediction() -> None:
    logits = torch.tensor([[[[10.0, -10.0], [10.0, -10.0]]]])
    target = torch.tensor([[[[1.0, 0.0], [1.0, 0.0]]]])
    assert dice_score(logits, target) == 1.0


def test_iou_score_partial_overlap() -> None:
    logits = torch.tensor([[[[10.0, 10.0], [-10.0, -10.0]]]])
    target = torch.tensor([[[[1.0, 0.0], [1.0, 0.0]]]])
    assert iou_score(logits, target) == 1 / 3
