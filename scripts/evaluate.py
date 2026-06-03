from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import albumentations as A
import numpy as np
import torch
import yaml
from PIL import Image
from torch.utils.data import DataLoader

from src.ukan_course.datasets.segmentation_dataset import SegmentationDataset
from src.ukan_course.metrics import binary_stats, scores_from_stats
from src.ukan_course.models import AttentionUKAN, UKAN, UNet
from src.ukan_course.utils import count_parameters, ensure_dir, read_split, seed_everything


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate U-KAN segmentation models.")
    parser.add_argument("--name", required=True, help="Experiment name under output-dir.")
    parser.add_argument("--output-dir", default="experiments/results")
    return parser.parse_args()


def load_config(exp_dir: Path) -> dict:
    with (exp_dir / "config.yml").open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_model(config: dict) -> torch.nn.Module:
    if config["model"] == "unet":
        return UNet(
            num_classes=1,
            input_channels=3,
            base_channels=config.get("base_channels", 32),
        )
    model_cls = AttentionUKAN if config["model"] == "attention_ukan" else UKAN
    return model_cls(
        num_classes=1,
        input_channels=3,
        embed_dims=config["embed_dims"],
        no_kan=config["no_kan"],
    )


def build_loader(config: dict) -> DataLoader:
    ids = read_split(config["val_split"])
    transform = A.Compose([A.Resize(config["input_size"], config["input_size"])])
    dataset = SegmentationDataset(
        image_ids=ids,
        image_dir=Path(config["data_dir"]) / "images",
        mask_dir=Path(config["data_dir"]) / "masks" / "0",
        image_ext=".png",
        mask_ext=config["mask_ext"],
        transform=transform,
    )
    return DataLoader(
        dataset,
        batch_size=config["batch_size"],
        shuffle=False,
        num_workers=config.get("num_workers", 0),
        drop_last=False,
    )


def main() -> int:
    args = parse_args()
    exp_dir = Path(args.output_dir) / args.name
    config = load_config(exp_dir)
    seed_everything(config["seed"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(config).to(device)
    checkpoint = torch.load(exp_dir / "model.pth", map_location=device)
    model.load_state_dict(checkpoint)
    model.eval()

    loader = build_loader(config)
    pred_dir = ensure_dir(exp_dir / "predictions")
    total_stats = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    total_infer_seconds = 0.0
    total_samples = 0

    with torch.no_grad():
        for images, masks, meta in loader:
            images = images.to(device)
            masks = masks.to(device)
            if device.type == "cuda":
                torch.cuda.synchronize()
            start_time = time.perf_counter()
            logits = model(images)
            if device.type == "cuda":
                torch.cuda.synchronize()
            total_infer_seconds += time.perf_counter() - start_time
            batch_size = images.size(0)
            batch_stats = binary_stats(logits, masks)
            for key, value in batch_stats.items():
                total_stats[key] += value
            total_samples += batch_size

            probs = torch.sigmoid(logits).cpu().numpy()
            preds = (probs >= 0.5).astype(np.uint8) * 255
            for pred, image_id in zip(preds, meta["image_id"]):
                Image.fromarray(pred[0], mode="L").save(pred_dir / f"{image_id}.png")

    scores = scores_from_stats(total_stats)
    metrics = {
        "name": config["name"],
        "dataset": config["dataset"],
        "model": config["model"],
        "seed": config["seed"],
        "iou": scores["iou"],
        "dice": scores["dice"],
        "precision": scores["precision"],
        "recall": scores["recall"],
        "specificity": scores["specificity"],
        "params": count_parameters(model),
        "infer_ms_per_image": 1000.0 * total_infer_seconds / max(total_samples, 1),
    }

    with (exp_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)

    print(
        f"name={metrics['name']} dataset={metrics['dataset']} model={metrics['model']} "
        f"iou={metrics['iou']:.4f} dice={metrics['dice']:.4f} "
        f"precision={metrics['precision']:.4f} recall={metrics['recall']:.4f} "
        f"params={metrics['params']} infer_ms={metrics['infer_ms_per_image']:.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
