from __future__ import annotations

import argparse
import shutil
from pathlib import Path


VALID_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}


def normalized_name(path: Path) -> str:
    safe = path.stem.replace(" ", "_").replace("(", "").replace(")", "")
    return safe.lower()


def prepare_busi(raw_dir: Path, out_dir: Path) -> int:
    image_out = out_dir / "busi" / "images"
    mask_out = out_dir / "busi" / "masks" / "0"
    image_out.mkdir(parents=True, exist_ok=True)
    mask_out.mkdir(parents=True, exist_ok=True)

    copied = 0
    for path in raw_dir.rglob("*"):
        if path.suffix.lower() not in VALID_IMAGE_EXTS:
            continue
        if "mask" in path.stem.lower():
            continue
        mask_candidates = list(path.parent.glob(f"{path.stem}*mask*{path.suffix}"))
        if not mask_candidates:
            continue
        case_id = normalized_name(path)
        shutil.copy2(path, image_out / f"{case_id}.png")
        shutil.copy2(mask_candidates[0], mask_out / f"{case_id}_mask.png")
        copied += 1
    print(f"prepared_busi_cases={copied}")
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
