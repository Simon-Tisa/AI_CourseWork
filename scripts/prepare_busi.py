from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


VALID_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}


def normalized_name(path: Path) -> str:
    safe = path.stem.replace(" ", "_").replace("(", "").replace(")", "")
    return safe.lower()


def find_mask_candidates(image_path: Path) -> list[Path]:
    candidates: list[Path] = []
    for suffix in VALID_IMAGE_EXTS:
        candidates.extend(image_path.parent.glob(f"{image_path.stem}*mask*{suffix}"))
    return sorted(candidates, key=lambda path: path.name.lower())


def save_image_as_png(src_path: Path, dst_path: Path) -> None:
    with Image.open(src_path) as image:
        image.convert("RGB").save(dst_path)


def save_combined_mask(mask_paths: list[Path], dst_path: Path) -> None:
    combined: np.ndarray | None = None
    base_size: tuple[int, int] | None = None

    for mask_path in mask_paths:
        with Image.open(mask_path) as mask:
            if base_size is None:
                base_size = mask.size
            elif mask.size != base_size:
                mask = mask.resize(base_size, Image.Resampling.NEAREST)
            mask_array = np.asarray(mask.convert("L")) > 0

        if combined is None:
            combined = mask_array
        else:
            combined = np.logical_or(combined, mask_array)

    if combined is None:
        raise ValueError("No masks were provided for combination.")

    Image.fromarray((combined.astype(np.uint8) * 255), mode="L").save(dst_path)


def prepare_busi(raw_dir: Path, out_dir: Path) -> int:
    image_out = out_dir / "busi" / "images"
    mask_out = out_dir / "busi" / "masks" / "0"
    image_out.mkdir(parents=True, exist_ok=True)
    mask_out.mkdir(parents=True, exist_ok=True)

    copied = 0
    merged_multi_mask_cases = 0
    for path in raw_dir.rglob("*"):
        if path.suffix.lower() not in VALID_IMAGE_EXTS:
            continue
        if "mask" in path.stem.lower():
            continue
        mask_candidates = find_mask_candidates(path)
        if not mask_candidates:
            continue
        case_id = normalized_name(path)
        save_image_as_png(path, image_out / f"{case_id}.png")
        save_combined_mask(mask_candidates, mask_out / f"{case_id}_mask.png")
        if len(mask_candidates) > 1:
            merged_multi_mask_cases += 1
        copied += 1

    print(f"prepared_busi_cases={copied}")
    print(f"merged_multi_mask_cases={merged_multi_mask_cases}")
    return copied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--out-dir", default="data/processed")
    args = parser.parse_args()
    count = prepare_busi(Path(args.raw_dir), Path(args.out_dir))
    return 0 if count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
