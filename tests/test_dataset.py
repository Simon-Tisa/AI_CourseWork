from __future__ import annotations

from pathlib import Path

from scripts.make_splits import split_ids


def test_split_ids_is_deterministic() -> None:
    ids = [f"case_{idx:03d}" for idx in range(10)]
    first_train, first_val = split_ids(ids, val_ratio=0.2, seed=2981)
    second_train, second_val = split_ids(ids, val_ratio=0.2, seed=2981)
    assert first_train == second_train
    assert first_val == second_val
    assert len(first_train) == 8
    assert len(first_val) == 2
    assert set(first_train).isdisjoint(second_val)


def test_split_ids_rejects_empty_input() -> None:
    try:
        split_ids([], val_ratio=0.2, seed=2981)
    except ValueError as exc:
        assert "at least two image ids" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty input")


def test_project_paths_are_not_raw_course_materials() -> None:
    project_root = Path(__file__).resolve().parents[1]
    assert project_root.name == "ukan-course-paper"
