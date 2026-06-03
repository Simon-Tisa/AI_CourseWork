from __future__ import annotations

import torch

from src.ukan_course.metrics import binary_stats, dice_score, iou_score, scores_from_stats


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


def test_scores_from_binary_stats() -> None:
    logits = torch.tensor([[[[10.0, 10.0], [-10.0, -10.0]]]])
    target = torch.tensor([[[[1.0, 0.0], [1.0, 0.0]]]])
    stats = binary_stats(logits, target)
    scores = scores_from_stats(stats)
    assert stats == {"tp": 1, "fp": 1, "fn": 1, "tn": 1}
    assert scores["iou"] == 1 / 3
    assert scores["precision"] == 0.5
    assert scores["recall"] == 0.5
