from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


VALID_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def resolve_cvc_dirs(raw_dir: Path) -> tuple[Path, Path]:
    candidate_pairs = [
        (raw_dir / "PNG" / "Original", raw_dir / "PNG" / "Ground Truth"),
        (raw_dir / "Original", raw_dir / "Ground Truth"),
        (raw_dir / "images", raw_dir / "masks"),
        (raw_dir / "Original", raw_dir / "GT"),
        (raw_dir / "TIF" / "Original", raw_dir / "TIF" / "Ground Truth"),
    ]
    for image_dir, mask_dir in candidate_pairs:
        if image_dir.exists() and mask_dir.exists():
            return image_dir, mask_dir
    return raw_dir, raw_dir


def find_matching_mask(mask_dir: Path, image_path: Path) -> Path | None:
    exact_path = mask_dir / image_path.name
    if exact_path.exists():
        return exact_path

    for suffix in VALID_IMAGE_EXTS:
        candidate = mask_dir / f"{image_path.stem}{suffix}"
        if candidate.exists():
            return candidate
    return None


def save_image_as_png(src_path: Path, dst_path: Path) -> None:
    with Image.open(src_path) as image:
        image.convert("RGB").save(dst_path)


def save_binary_mask_as_png(src_path: Path, dst_path: Path) -> None:
    with Image.open(src_path) as mask:
        mask_array = np.asarray(mask.convert("L")) > 0
    Image.fromarray((mask_array.astype(np.uint8) * 255), mode="L").save(dst_path)


def prepare_cvc(raw_dir: Path, out_dir: Path) -> int:
    image_dir, mask_dir = resolve_cvc_dirs(raw_dir)

    image_out = out_dir / "cvc" / "images"
    mask_out = out_dir / "cvc" / "masks" / "0"
    image_out.mkdir(parents=True, exist_ok=True)
    mask_out.mkdir(parents=True, exist_ok=True)

    copied = 0
    for image_path in sorted(image_dir.iterdir(), key=lambda path: path.name.lower()):
        if image_path.suffix.lower() not in VALID_IMAGE_EXTS:
            continue
        mask_path = find_matching_mask(mask_dir, image_path)
        if mask_path is None:
            continue
        case_id = image_path.stem.lower()
        save_image_as_png(image_path, image_out / f"{case_id}.png")
        save_binary_mask_as_png(mask_path, mask_out / f"{case_id}.png")
        copied += 1

    print(f"cvc_image_dir={image_dir}")
    print(f"cvc_mask_dir={mask_dir}")
    print(f"prepared_cvc_cases={copied}")
    return copied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--out-dir", default="data/processed")
    args = parser.parse_args()
    count = prepare_cvc(Path(args.raw_dir), Path(args.out_dir))
    return 0 if count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
