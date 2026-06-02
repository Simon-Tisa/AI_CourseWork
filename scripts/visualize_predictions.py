from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from PIL import Image

from src.ukan_course.utils import read_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize U-KAN and Attention-U-KAN predictions.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--ukan-name", required=True)
    parser.add_argument("--attention-name", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--max-samples", type=int, default=4)
    return parser.parse_args()


def load_config(exp_dir: Path) -> dict:
    with (exp_dir / "config.yml").open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def load_gray(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"))


def error_map(pred: np.ndarray, gt: np.ndarray) -> np.ndarray:
    pred_bin = pred > 127
    gt_bin = gt > 127
    out = np.zeros((*gt.shape, 3), dtype=np.uint8)
    out[np.logical_and(pred_bin, gt_bin)] = [255, 255, 255]
    out[np.logical_and(pred_bin, ~gt_bin)] = [255, 0, 0]
    out[np.logical_and(~pred_bin, gt_bin)] = [0, 120, 255]
    return out


def main() -> int:
    args = parse_args()
    base = Path(args.output_dir)
    ukan_dir = base / args.ukan_name
    attention_dir = base / args.attention_name
    config = load_config(ukan_dir)
    image_dir = Path(config["data_dir"]) / "images"
    mask_dir = Path(config["data_dir"]) / "masks" / "0"
    ids = read_split(config["val_split"])[: args.max_samples]

    fig, axes = plt.subplots(len(ids), 5, figsize=(15, 3 * len(ids)))
    if len(ids) == 1:
        axes = np.expand_dims(axes, axis=0)

    for row, image_id in enumerate(ids):
        image = load_rgb(image_dir / f"{image_id}.png")
        gt = load_gray(mask_dir / f"{image_id}{config['mask_ext']}")
        ukan_pred = load_gray(ukan_dir / "predictions" / f"{image_id}.png")
        attention_pred = load_gray(attention_dir / "predictions" / f"{image_id}.png")
        err = error_map(attention_pred, gt)

        panels = [
            (image, "Image", None),
            (gt, "Ground Truth", "gray"),
            (ukan_pred, "U-KAN", "gray"),
            (attention_pred, "Attention-U-KAN", "gray"),
            (err, "Error Map", None),
        ]
        for col, (panel, title, cmap) in enumerate(panels):
            axes[row, col].imshow(panel, cmap=cmap)
            axes[row, col].set_title(title)
            axes[row, col].axis("off")

    fig.tight_layout()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"wrote_figure={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
