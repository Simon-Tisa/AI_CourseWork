from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize experiment metrics into a paper table.")
    parser.add_argument("--results-dir", default="experiments/results")
    parser.add_argument("--out", default="paper/tables/segmentation_results.csv")
    return parser.parse_args()


def variant_label(row: dict[str, str]) -> str:
    name = row.get("name", "")
    model = row.get("model", "")
    if model == "unet":
        return "U-Net"
    if model == "attention_ukan":
        return "Attention-U-KAN"
    if "no_kan" in name:
        return "U-KAN(no-KAN)"
    if model == "ukan":
        return "U-KAN"
    return model


def main() -> int:
    args = parse_args()
    rows: list[dict[str, str]] = []
    for metrics_path in sorted(Path(args.results_dir).glob("*/metrics.csv")):
        with metrics_path.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows.extend(reader)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "name",
            "dataset",
            "variant",
            "model",
            "seed",
            "iou",
            "dice",
            "precision",
            "recall",
            "specificity",
            "params",
            "infer_ms_per_image",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row["variant"] = variant_label(row)
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    print(f"wrote_table={out} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
