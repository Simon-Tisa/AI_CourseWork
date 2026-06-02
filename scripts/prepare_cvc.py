from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def prepare_cvc(raw_dir: Path, out_dir: Path) -> int:
    image_candidates = [raw_dir / "Original", raw_dir / "images", raw_dir]
    mask_candidates = [raw_dir / "Ground Truth", raw_dir / "masks", raw_dir / "GT"]
    image_dir = next((path for path in image_candidates if path.exists()), raw_dir)
    mask_dir = next((path for path in mask_candidates if path.exists()), raw_dir)

    image_out = out_dir / "cvc" / "images"
    mask_out = out_dir / "cvc" / "masks" / "0"
    image_out.mkdir(parents=True, exist_ok=True)
    mask_out.mkdir(parents=True, exist_ok=True)

    copied = 0
    for image_path in sorted(image_dir.glob("*.png")):
        mask_path = mask_dir / image_path.name
        if not mask_path.exists():
            continue
        case_id = image_path.stem.lower()
        shutil.copy2(image_path, image_out / f"{case_id}.png")
        shutil.copy2(mask_path, mask_out / f"{case_id}.png")
        copied += 1
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
