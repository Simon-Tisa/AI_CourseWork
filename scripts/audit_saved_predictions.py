from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "experiments" / "tables" / "segmentation_results.csv"
OUTPUT_PATH = ROOT / "matlab_figures" / "output" / "opencv_prediction_audit.csv"


def safe_divide(numerator: int, denominator: int) -> float:
    return 1.0 if denominator == 0 else numerator / denominator


def main() -> int:
    with SUMMARY_PATH.open(encoding="utf-8", newline="") as file:
        summary = list(csv.DictReader(file))

    audit_rows: list[dict[str, str | int | float]] = []
    for row in summary:
        name = row["name"]
        dataset = row["dataset"]
        seed = row["seed"]
        split_path = ROOT / "data" / "splits" / f"{dataset}_seed{seed}_val.txt"
        image_ids = [
            value.strip()
            for value in split_path.read_text(encoding="utf-8").splitlines()
            if value.strip()
        ]
        mask_ext = "_mask.png" if dataset == "busi" else ".png"
        stats = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

        for image_id in image_ids:
            mask_path = (
                ROOT
                / "data"
                / "processed"
                / dataset
                / "masks"
                / "0"
                / f"{image_id}{mask_ext}"
            )
            prediction_path = (
                ROOT
                / "experiments"
                / "results"
                / name
                / "predictions"
                / f"{image_id}.png"
            )
            ground_truth = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            prediction = cv2.imread(str(prediction_path), cv2.IMREAD_GRAYSCALE)
            if ground_truth is None or prediction is None:
                raise FileNotFoundError(f"Missing mask or prediction for {name}/{image_id}")

            ground_truth = cv2.resize(
                ground_truth,
                (256, 256),
                interpolation=cv2.INTER_NEAREST,
            )
            ground_truth = ground_truth.astype(np.float32) / 255.0 >= 0.5
            prediction = prediction >= 128
            stats["tp"] += int(np.logical_and(prediction, ground_truth).sum())
            stats["fp"] += int(np.logical_and(prediction, ~ground_truth).sum())
            stats["fn"] += int(np.logical_and(~prediction, ground_truth).sum())
            stats["tn"] += int(np.logical_and(~prediction, ~ground_truth).sum())

        tp, fp, fn, tn = (stats[key] for key in ("tp", "fp", "fn", "tn"))
        recomputed = {
            "iou": safe_divide(tp, tp + fp + fn),
            "dice": safe_divide(2 * tp, 2 * tp + fp + fn),
            "precision": safe_divide(tp, tp + fp),
            "recall": safe_divide(tp, tp + fn),
            "specificity": safe_divide(tn, tn + fp),
        }
        max_difference = max(
            abs(recomputed[key] - float(row[key])) for key in recomputed
        )
        audit_rows.append(
            {
                "name": name,
                "dataset": dataset,
                "seed": seed,
                "samples": len(image_ids),
                **stats,
                **{f"recomputed_{key}": value for key, value in recomputed.items()},
                "max_abs_diff_vs_summary": max_difference,
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(audit_rows[0].keys()))
        writer.writeheader()
        writer.writerows(audit_rows)

    maximum = max(float(row["max_abs_diff_vs_summary"]) for row in audit_rows)
    if maximum > 1e-12:
        raise RuntimeError(f"Saved prediction audit failed: max difference={maximum}")
    print(
        f"saved_prediction_audit=PASS runs={len(audit_rows)} "
        f"samples={sum(int(row['samples']) for row in audit_rows)} "
        f"max_difference={maximum:.17g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
