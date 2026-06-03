from __future__ import annotations

import argparse
import csv
from pathlib import Path

import albumentations as A
import torch
import torch.optim as optim
import yaml
from torch.optim import lr_scheduler
from torch.utils.data import DataLoader

from src.ukan_course.datasets.segmentation_dataset import SegmentationDataset
from src.ukan_course.losses import BCEDiceLoss
from src.ukan_course.metrics import dice_score, iou_score
from src.ukan_course.models import AttentionUKAN, UKAN
from src.ukan_course.utils import count_parameters, ensure_dir, read_split, seed_everything

try:
    from tensorboardX import SummaryWriter
except ImportError:  # pragma: no cover
    SummaryWriter = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train U-KAN segmentation models.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--epochs", type=int, default=None, help="Override epochs from config.")
    parser.add_argument("--batch-size", type=int, default=None, help="Override batch_size from config.")
    parser.add_argument("--limit-train-batches", type=int, default=None)
    parser.add_argument("--limit-val-batches", type=int, default=None)
    return parser.parse_args()


def load_config(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_model(config: dict) -> torch.nn.Module:
    model_cls = AttentionUKAN if config["model"] == "attention_ukan" else UKAN
    return model_cls(
        num_classes=1,
        input_channels=3,
        embed_dims=config["embed_dims"],
        no_kan=config["no_kan"],
    )


def build_optimizer(model: torch.nn.Module, config: dict) -> torch.optim.Optimizer:
    param_groups = []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        is_kan_parameter = (
            not config.get("no_kan", False)
            and "layer" in name.lower()
            and "fc" in name.lower()
        )
        if is_kan_parameter:
            param_groups.append(
                {
                    "params": param,
                    "lr": config["kan_lr"],
                    "weight_decay": config["kan_weight_decay"],
                }
            )
        else:
            param_groups.append(
                {
                    "params": param,
                    "lr": config["lr"],
                    "weight_decay": config["weight_decay"],
                }
            )
    return optim.Adam(param_groups)


def build_transforms(config: dict, training: bool):
    transforms = []
    if training:
        transforms.extend([A.RandomRotate90(p=0.5), A.HorizontalFlip(p=0.5), A.VerticalFlip(p=0.5)])
    transforms.append(A.Resize(config["input_size"], config["input_size"]))
    return A.Compose(transforms)


def build_loader(config: dict, split_key: str, training: bool) -> DataLoader:
    ids = read_split(config[split_key])
    dataset = SegmentationDataset(
        image_ids=ids,
        image_dir=Path(config["data_dir"]) / "images",
        mask_dir=Path(config["data_dir"]) / "masks" / "0",
        image_ext=".png",
        mask_ext=config["mask_ext"],
        transform=build_transforms(config, training),
    )
    return DataLoader(
        dataset,
        batch_size=config["batch_size"],
        shuffle=training,
        num_workers=config.get("num_workers", 0),
        drop_last=False,
    )


def run_epoch(
    model: torch.nn.Module,
    loader: DataLoader,
    criterion: torch.nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
    max_batches: int | None = None,
) -> dict[str, float]:
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    total_iou = 0.0
    total_dice = 0.0
    total_samples = 0

    for batch_idx, (images, masks, _) in enumerate(loader):
        if max_batches is not None and batch_idx >= max_batches:
            break

        images = images.to(device)
        masks = masks.to(device)

        if training:
            optimizer.zero_grad()

        logits = model(images)
        loss = criterion(logits, masks)

        if training:
            loss.backward()
            optimizer.step()

        batch_size = images.size(0)
        total_loss += loss.item() * batch_size
        total_iou += iou_score(logits.detach(), masks.detach()) * batch_size
        total_dice += dice_score(logits.detach(), masks.detach()) * batch_size
        total_samples += batch_size

    return {
        "loss": total_loss / max(total_samples, 1),
        "iou": total_iou / max(total_samples, 1),
        "dice": total_dice / max(total_samples, 1),
    }


def append_log(path: Path, row: dict[str, float | int]) -> None:
    first_write = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["epoch", "lr", "loss", "iou", "dice", "val_loss", "val_iou", "val_dice"],
        )
        if first_write:
            writer.writeheader()
        writer.writerow(row)


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    if args.epochs is not None:
        config["epochs"] = args.epochs
    if args.batch_size is not None:
        config["batch_size"] = args.batch_size
    seed_everything(config["seed"])

    exp_dir = ensure_dir(Path(args.output_dir) / config["name"])
    with (exp_dir / "config.yml").open("w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, allow_unicode=True, sort_keys=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(config).to(device)
    criterion = BCEDiceLoss().to(device)
    optimizer = build_optimizer(model, config)
    scheduler = lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config["epochs"],
        eta_min=config["min_lr"],
    )
    train_loader = build_loader(config, "train_split", training=True)
    val_loader = build_loader(config, "val_split", training=False)
    writer = SummaryWriter(str(exp_dir)) if SummaryWriter is not None else None

    print(f"name={config['name']}")
    print(f"device={device}")
    print(f"params={count_parameters(model)}")

    best_iou = -1.0
    for epoch in range(config["epochs"]):
        train_log = run_epoch(
            model,
            train_loader,
            criterion,
            device,
            optimizer,
            max_batches=args.limit_train_batches,
        )
        with torch.no_grad():
            val_log = run_epoch(
                model,
                val_loader,
                criterion,
                device,
                optimizer=None,
                max_batches=args.limit_val_batches,
            )
        scheduler.step()

        row = {
            "epoch": epoch,
            "lr": optimizer.param_groups[0]["lr"],
            "loss": train_log["loss"],
            "iou": train_log["iou"],
            "dice": train_log["dice"],
            "val_loss": val_log["loss"],
            "val_iou": val_log["iou"],
            "val_dice": val_log["dice"],
        }
        append_log(exp_dir / "log.csv", row)

        if writer is not None:
            writer.add_scalar("train/loss", train_log["loss"], epoch)
            writer.add_scalar("train/iou", train_log["iou"], epoch)
            writer.add_scalar("train/dice", train_log["dice"], epoch)
            writer.add_scalar("val/loss", val_log["loss"], epoch)
            writer.add_scalar("val/iou", val_log["iou"], epoch)
            writer.add_scalar("val/dice", val_log["dice"], epoch)

        print(
            f"epoch={epoch:03d} loss={train_log['loss']:.4f} iou={train_log['iou']:.4f} "
            f"val_loss={val_log['loss']:.4f} val_iou={val_log['iou']:.4f} val_dice={val_log['dice']:.4f}"
        )

        if val_log["iou"] > best_iou:
            best_iou = val_log["iou"]
            torch.save(model.state_dict(), exp_dir / "model.pth")
            print(f"saved_best_model val_iou={best_iou:.4f}")

    if writer is not None:
        writer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
