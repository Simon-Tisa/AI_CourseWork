from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate dataset statistics and sample figures.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--out-results", default="experiments/results")
    parser.add_argument("--out-figures", default="experiments/figures")
    parser.add_argument("--max-samples", type=int, default=4)
    return parser.parse_args()


def mask_ext_for(dataset: str) -> str:
    return "_mask.png" if dataset.lower() == "busi" else ".png"


def load_image(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def load_mask(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"))


def overlay_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    overlay = image.copy()
    overlay[mask > 127] = (0.55 * overlay[mask > 127] + np.array([255, 0, 0]) * 0.45).astype(np.uint8)
    return overlay


def fit_tile(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    tile = Image.new("RGB", size, "white")
    fitted = image.copy()
    fitted.thumbnail(size, Image.Resampling.LANCZOS)
    offset = ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2)
    tile.paste(fitted, offset)
    return tile


def save_samples_with_pillow(
    sample_paths: list[Path],
    mask_dir: Path,
    mask_ext: str,
    figure_path: Path,
    tile_size: tuple[int, int] = (256, 256),
) -> None:
    labels = ("Image", "Mask", "Overlay")
    label_height = 24
    rows = len(sample_paths)
    canvas = Image.new("RGB", (tile_size[0] * 3, rows * (tile_size[1] + label_height)), "white")
    draw = ImageDraw.Draw(canvas)

    for row, image_path in enumerate(sample_paths):
        image = load_image(image_path)
        mask = load_mask(mask_dir / f"{image_path.stem}{mask_ext}")
        tiles = [
            Image.fromarray(image),
            Image.fromarray(mask).convert("RGB"),
            Image.fromarray(overlay_mask(image, mask)),
        ]
        y = row * (tile_size[1] + label_height)
        for col, label in enumerate(labels):
            x = col * tile_size[0]
            draw.text((x + 8, y + 4), label, fill=(30, 30, 30))
            canvas.paste(fit_tile(tiles[col], tile_size), (x, y + label_height))

    canvas.save(figure_path)


def save_samples_with_matplotlib(
    sample_paths: list[Path],
    mask_dir: Path,
    mask_ext: str,
    figure_path: Path,
) -> None:
    if plt is None:
        save_samples_with_pillow(sample_paths, mask_dir, mask_ext, figure_path)
        return

    fig, axes = plt.subplots(len(sample_paths), 3, figsize=(9, 3 * len(sample_paths)))
    if len(sample_paths) == 1:
        axes = np.expand_dims(axes, axis=0)
    for row, image_path in enumerate(sample_paths):
        image = load_image(image_path)
        mask = load_mask(mask_dir / f"{image_path.stem}{mask_ext}")
        axes[row, 0].imshow(image)
        axes[row, 0].set_title("Image")
        axes[row, 1].imshow(mask, cmap="gray")
        axes[row, 1].set_title("Mask")
        axes[row, 2].imshow(overlay_mask(image, mask))
        axes[row, 2].set_title("Overlay")
        for col in range(3):
            axes[row, col].axis("off")

    fig.tight_layout()
    fig.savefig(figure_path, dpi=200)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    root = Path(args.data_dir) / args.dataset
    image_dir = root / "images"
    mask_dir = root / "masks" / "0"
    image_paths = sorted(image_dir.glob("*.png"))
    if not image_paths:
        raise FileNotFoundError(f"No images found in {image_dir}")

    widths: list[int] = []
    heights: list[int] = []
    mask_ratios: list[float] = []
    ext = mask_ext_for(args.dataset)

    for image_path in image_paths:
        image = Image.open(image_path)
        widths.append(image.width)
        heights.append(image.height)
        mask = load_mask(mask_dir / f"{image_path.stem}{ext}")
        mask_ratios.append(float((mask > 127).mean()))

    out_results = Path(args.out_results)
    out_results.mkdir(parents=True, exist_ok=True)
    stats_path = out_results / f"{args.dataset}_dataset_stats.csv"
    with stats_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "dataset",
                "num_images",
                "min_width",
                "max_width",
                "min_height",
                "max_height",
                "mean_mask_ratio",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "dataset": args.dataset,
                "num_images": len(image_paths),
                "min_width": min(widths),
                "max_width": max(widths),
                "min_height": min(heights),
                "max_height": max(heights),
                "mean_mask_ratio": sum(mask_ratios) / len(mask_ratios),
            }
        )

    out_figures = Path(args.out_figures)
    out_figures.mkdir(parents=True, exist_ok=True)
    figure_path = out_figures / f"{args.dataset}_samples.png"
    sample_paths = image_paths[: args.max_samples]
    save_samples_with_matplotlib(sample_paths, mask_dir, ext, figure_path)
    print(f"wrote_stats={stats_path}")
    print(f"wrote_figure={figure_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
