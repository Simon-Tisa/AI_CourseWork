from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import yaml
from PIL import Image, ImageDraw

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

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


def fit_tile(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    tile = Image.new("RGB", size, "white")
    fitted = image.copy()
    fitted.thumbnail(size, Image.Resampling.LANCZOS)
    offset = ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2)
    tile.paste(fitted, offset)
    return tile


def panel_to_image(panel: np.ndarray) -> Image.Image:
    return Image.fromarray(panel).convert("RGB")


def save_with_pillow(rows: list[list[tuple[np.ndarray, str]]], out: Path) -> None:
    tile_size = (240, 240)
    label_height = 24
    cols = len(rows[0])
    canvas = Image.new(
        "RGB",
        (cols * tile_size[0], len(rows) * (tile_size[1] + label_height)),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    for row_idx, row in enumerate(rows):
        y = row_idx * (tile_size[1] + label_height)
        for col_idx, (panel, title) in enumerate(row):
            x = col_idx * tile_size[0]
            draw.text((x + 8, y + 4), title, fill=(30, 30, 30))
            canvas.paste(fit_tile(panel_to_image(panel), tile_size), (x, y + label_height))
    canvas.save(out)


def save_with_matplotlib(rows: list[list[tuple[np.ndarray, str]]], out: Path) -> None:
    if plt is None:
        save_with_pillow(rows, out)
        return

    fig, axes = plt.subplots(len(rows), len(rows[0]), figsize=(15, 3 * len(rows)))
    if len(rows) == 1:
        axes = np.expand_dims(axes, axis=0)

    for row_idx, row in enumerate(rows):
        for col_idx, (panel, title) in enumerate(row):
            cmap = "gray" if panel.ndim == 2 else None
            axes[row_idx, col_idx].imshow(panel, cmap=cmap)
            axes[row_idx, col_idx].set_title(title)
            axes[row_idx, col_idx].axis("off")

    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    base = Path(args.output_dir)
    ukan_dir = base / args.ukan_name
    attention_dir = base / args.attention_name
    config = load_config(ukan_dir)
    image_dir = Path(config["data_dir"]) / "images"
    mask_dir = Path(config["data_dir"]) / "masks" / "0"
    ids = read_split(config["val_split"])[: args.max_samples]

    rows: list[list[tuple[np.ndarray, str]]] = []
    for row, image_id in enumerate(ids):
        image = load_rgb(image_dir / f"{image_id}.png")
        gt = load_gray(mask_dir / f"{image_id}{config['mask_ext']}")
        ukan_pred = load_gray(ukan_dir / "predictions" / f"{image_id}.png")
        attention_pred = load_gray(attention_dir / "predictions" / f"{image_id}.png")
        err = error_map(attention_pred, gt)

        rows.append(
            [
                (image, "Image"),
                (gt, "Ground Truth"),
                (ukan_pred, "U-KAN"),
                (attention_pred, "Attention-U-KAN"),
                (err, "Error Map"),
            ]
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    save_with_matplotlib(rows, out)
    print(f"wrote_figure={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
