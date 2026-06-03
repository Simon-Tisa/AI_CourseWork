from __future__ import annotations

import numpy as np
from PIL import Image

from scripts.prepare_busi import prepare_busi
from scripts.prepare_cvc import prepare_cvc


def save_rgb(path, value: int = 64) -> None:
    Image.fromarray(np.full((4, 4, 3), value, dtype=np.uint8), mode="RGB").save(path)


def save_mask(path, coords: list[tuple[int, int]]) -> None:
    mask = np.zeros((4, 4), dtype=np.uint8)
    for row, col in coords:
        mask[row, col] = 255
    Image.fromarray(mask, mode="L").save(path)


def test_prepare_busi_merges_multiple_masks(tmp_path) -> None:
    raw_dir = tmp_path / "raw" / "Dataset_BUSI_with_GT" / "benign"
    raw_dir.mkdir(parents=True)
    save_rgb(raw_dir / "benign (1).png")
    save_mask(raw_dir / "benign (1)_mask.png", [(0, 0)])
    save_mask(raw_dir / "benign (1)_mask_1.png", [(3, 3)])

    assert prepare_busi(tmp_path / "raw", tmp_path / "processed") == 1

    with Image.open(
        tmp_path / "processed" / "busi" / "masks" / "0" / "benign_1_mask.png"
    ) as merged_mask:
        merged = np.asarray(merged_mask)
    assert merged[0, 0] == 255
    assert merged[3, 3] == 255


def test_prepare_cvc_detects_nested_png_layout(tmp_path) -> None:
    image_dir = tmp_path / "raw" / "PNG" / "Original"
    mask_dir = tmp_path / "raw" / "PNG" / "Ground Truth"
    image_dir.mkdir(parents=True)
    mask_dir.mkdir(parents=True)
    save_rgb(image_dir / "1.png")
    save_mask(mask_dir / "1.png", [(1, 1)])

    assert prepare_cvc(tmp_path / "raw", tmp_path / "processed") == 1
    assert (tmp_path / "processed" / "cvc" / "images" / "1.png").exists()
    assert (tmp_path / "processed" / "cvc" / "masks" / "0" / "1.png").exists()
