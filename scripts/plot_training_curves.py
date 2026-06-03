from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot training curves from experiment log.csv files.")
    parser.add_argument("--names", nargs="+", required=True, help="Experiment names under output-dir.")
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def read_log(path: Path) -> list[dict[str, float]]:
    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [{key: float(value) for key, value in row.items()} for row in reader]


def load_runs(output_dir: Path, names: list[str]) -> dict[str, list[dict[str, float]]]:
    runs = {}
    for name in names:
        log_path = output_dir / name / "log.csv"
        if not log_path.exists():
            raise FileNotFoundError(f"Missing training log: {log_path}")
        runs[name] = read_log(log_path)
    return runs


def plot_with_matplotlib(runs: dict[str, list[dict[str, float]]], out: Path) -> None:
    if plt is None:
        plot_with_pillow(runs, out)
        return

    panels = [
        ("loss", "val_loss", "Loss"),
        ("iou", "val_iou", "IoU"),
        ("dice", "val_dice", "Dice"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for axis, (train_key, val_key, title) in zip(axes, panels):
        for name, rows in runs.items():
            epochs = [row["epoch"] for row in rows]
            axis.plot(epochs, [row[train_key] for row in rows], linestyle="--", label=f"{name} train")
            axis.plot(epochs, [row[val_key] for row in rows], label=f"{name} val")
        axis.set_title(title)
        axis.set_xlabel("Epoch")
        axis.grid(True, alpha=0.25)
    axes[-1].legend(fontsize=7, loc="best")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def normalize(values: list[float], low: float, high: float, pixel_low: int, pixel_high: int) -> list[int]:
    span = max(high - low, 1e-12)
    return [int(pixel_high - (value - low) / span * (pixel_high - pixel_low)) for value in values]


def draw_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    title: str,
    series: list[tuple[str, list[float], tuple[int, int, int]]],
) -> None:
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box
    pad_left, pad_top, pad_right, pad_bottom = 48, 30, 16, 34
    plot_box = (x0 + pad_left, y0 + pad_top, x1 - pad_right, y1 - pad_bottom)
    draw.rectangle(box, outline=(220, 220, 220))
    draw.text((x0 + 8, y0 + 6), title, fill=(20, 20, 20))
    draw.line((plot_box[0], plot_box[3], plot_box[2], plot_box[3]), fill=(90, 90, 90))
    draw.line((plot_box[0], plot_box[1], plot_box[0], plot_box[3]), fill=(90, 90, 90))

    all_values = [value for _, values, _ in series for value in values]
    low, high = min(all_values), max(all_values)
    max_len = max(len(values) for _, values, _ in series)
    x_span = max(max_len - 1, 1)

    for label, values, color in series:
        xs = [
            int(plot_box[0] + idx / x_span * (plot_box[2] - plot_box[0]))
            for idx in range(len(values))
        ]
        ys = normalize(values, low, high, plot_box[1], plot_box[3])
        points = list(zip(xs, ys))
        if len(points) >= 2:
            draw.line(points, fill=color, width=2)
        elif points:
            x, y = points[0]
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color)

    draw.text((plot_box[0], plot_box[3] + 8), "epoch", fill=(60, 60, 60))
    draw.text((x0 + 8, plot_box[1]), f"{high:.3f}", fill=(60, 60, 60))
    draw.text((x0 + 8, plot_box[3] - 10), f"{low:.3f}", fill=(60, 60, 60))


def plot_with_pillow(runs: dict[str, list[dict[str, float]]], out: Path) -> None:
    colors = [
        (31, 119, 180),
        (255, 127, 14),
        (44, 160, 44),
        (214, 39, 40),
        (148, 103, 189),
        (140, 86, 75),
        (227, 119, 194),
        (127, 127, 127),
    ]
    panels = [
        ("Loss", "val_loss"),
        ("Validation IoU", "val_iou"),
        ("Validation Dice", "val_dice"),
    ]
    width, height = 1500, 460
    canvas = Image.new("RGB", (width, height), "white")
    panel_width = width // 3

    for idx, (title, key) in enumerate(panels):
        series = []
        for color_idx, (name, rows) in enumerate(runs.items()):
            series.append((name, [row[key] for row in rows], colors[color_idx % len(colors)]))
        draw_panel(
            canvas,
            (idx * panel_width + 8, 16, (idx + 1) * panel_width - 8, height - 72),
            title,
            series,
        )

    draw = ImageDraw.Draw(canvas)
    legend_y = height - 46
    legend_x = 16
    for color_idx, name in enumerate(runs):
        color = colors[color_idx % len(colors)]
        draw.rectangle((legend_x, legend_y + 4, legend_x + 20, legend_y + 14), fill=color)
        draw.text((legend_x + 26, legend_y), name, fill=(30, 30, 30))
        legend_x += 220
    canvas.save(out)


def main() -> int:
    args = parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    runs = load_runs(Path(args.output_dir), args.names)
    plot_with_matplotlib(runs, out)
    print(f"wrote_figure={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
