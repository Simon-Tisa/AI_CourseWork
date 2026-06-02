from __future__ import annotations

import argparse
import csv
from pathlib import Path

import albumentations as A
import numpy as np
import torch
import yaml
from PIL import Image
from torch.utils.data import DataLoader

from src.ukan_course.datasets.segmentation_dataset import SegmentationDataset
from src.ukan_course.metrics import dice_score, iou_score
from src.ukan_course.models import AttentionUKAN, UKAN
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
    total_iou = 0.0
    total_dice = 0.0
    total_samples = 0

    with torch.no_grad():
        for images, masks, meta in loader:
            images = images.to(device)
            masks = masks.to(device)
            logits = model(images)
            batch_size = images.size(0)
            total_iou += iou_score(logits, masks) * batch_size
            total_dice += dice_score(logits, masks) * batch_size
            total_samples += batch_size

            probs = torch.sigmoid(logits).cpu().numpy()
            preds = (probs >= 0.5).astype(np.uint8) * 255
            for pred, image_id in zip(preds, meta["image_id"]):
                Image.fromarray(pred[0], mode="L").save(pred_dir / f"{image_id}.png")

    metrics = {
        "name": config["name"],
        "dataset": config["dataset"],
        "model": config["model"],
        "seed": config["seed"],
        "iou": total_iou / max(total_samples, 1),
        "dice": total_dice / max(total_samples, 1),
        "params": count_parameters(model),
    }

    with (exp_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)

    print(
        f"name={metrics['name']} dataset={metrics['dataset']} model={metrics['model']} "
        f"iou={metrics['iou']:.4f} dice={metrics['dice']:.4f} params={metrics['params']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
