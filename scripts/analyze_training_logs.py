from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze training curves for convergence and stability.")
    parser.add_argument("--results-dir", default="experiments/results")
    parser.add_argument("--out", default="paper/tables/training_diagnostics.csv")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def read_single_csv(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    return rows[0] if rows else {}


def to_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def analyze_run(run_dir: Path) -> dict[str, str] | None:
    log_path = run_dir / "log.csv"
    if not log_path.exists():
        return None

    rows = read_csv(log_path)
    if not rows:
        return None

    metrics = read_single_csv(run_dir / "metrics.csv") if (run_dir / "metrics.csv").exists() else {}
    best = max(rows, key=lambda row: to_float(row, "val_iou"))
    final = rows[-1]

    max_jump_epoch = ""
    max_jump = 0.0
    if len(rows) >= 2:
        jumps = [
            (int(rows[idx]["epoch"]), to_float(rows[idx], "val_iou") - to_float(rows[idx - 1], "val_iou"))
            for idx in range(1, len(rows))
        ]
        max_jump_epoch, max_jump = max(jumps, key=lambda item: item[1])

    window_start = rows[-10] if len(rows) >= 10 else rows[0]
    last_window_delta = to_float(final, "val_iou") - to_float(window_start, "val_iou")
    evaluate_iou = metrics.get("iou", "")
    evaluate_gap = ""
    if evaluate_iou:
        evaluate_gap = str(float(evaluate_iou) - to_float(best, "val_iou"))

    return {
        "name": run_dir.name,
        "dataset": metrics.get("dataset", ""),
        "model": metrics.get("model", ""),
        "seed": metrics.get("seed", ""),
        "epochs": str(len(rows)),
        "best_epoch": best["epoch"],
        "log_best_val_iou": best["val_iou"],
        "final_val_iou": final["val_iou"],
        "max_jump_epoch": str(max_jump_epoch),
        "max_positive_val_iou_jump": str(max_jump),
        "last10_val_iou_delta": str(last_window_delta),
        "evaluate_iou": evaluate_iou,
        "evaluate_minus_log_best_iou": evaluate_gap,
    }


def main() -> int:
    args = parse_args()
    results_dir = Path(args.results_dir)
    rows = [row for run_dir in sorted(results_dir.iterdir()) if run_dir.is_dir() for row in [analyze_run(run_dir)] if row]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "name",
        "dataset",
        "model",
        "seed",
        "epochs",
        "best_epoch",
        "log_best_val_iou",
        "final_val_iou",
        "max_jump_epoch",
        "max_positive_val_iou_jump",
        "last10_val_iou_delta",
        "evaluate_iou",
        "evaluate_minus_log_best_iou",
    ]
    with out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote_table={out} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
