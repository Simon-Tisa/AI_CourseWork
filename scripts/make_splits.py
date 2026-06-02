from __future__ import annotations

import argparse
import random
from pathlib import Path


def split_ids(image_ids: list[str], val_ratio: float, seed: int) -> tuple[list[str], list[str]]:
    if len(image_ids) < 2:
        raise ValueError("split_ids requires at least two image ids")
    if not 0 < val_ratio < 1:
        raise ValueError("val_ratio must be between 0 and 1")

    ids = sorted(image_ids)
    rng = random.Random(seed)
    rng.shuffle(ids)
    val_count = max(1, round(len(ids) * val_ratio))
    val_ids = sorted(ids[:val_count])
    train_ids = sorted(ids[val_count:])
    return train_ids, val_ids


def read_image_ids(image_dir: Path) -> list[str]:
    ids = [path.stem for path in image_dir.glob("*.png")]
    if not ids:
        raise ValueError(f"No .png images found in {image_dir}")
    return sorted(ids)


def write_ids(path: Path, ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(ids) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--split-dir", default="data/splits")
    parser.add_argument("--seed", type=int, default=2981)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    args = parser.parse_args()

    image_dir = Path(args.data_dir) / args.dataset / "images"
    image_ids = read_image_ids(image_dir)
    train_ids, val_ids = split_ids(image_ids, args.val_ratio, args.seed)
    split_dir = Path(args.split_dir)
    write_ids(split_dir / f"{args.dataset}_seed{args.seed}_train.txt", train_ids)
    write_ids(split_dir / f"{args.dataset}_seed{args.seed}_val.txt", val_ids)
    print(f"dataset={args.dataset} seed={args.seed} train={len(train_ids)} val={len(val_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
