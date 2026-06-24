from __future__ import annotations

from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
OUTPUT_DIR = ROOT / "paper" / "reference_figures"


def find_pdf(prefix: str) -> Path:
    matches = [
        path
        for path in WORKSPACE.rglob("*.pdf")
        if path.name.startswith(prefix)
    ]
    if not matches:
        raise FileNotFoundError(f"PDF not found: {prefix}")
    return min(matches, key=lambda path: len(str(path)))


def export_crop(
    pdf_prefix: str,
    page_number: int,
    bbox: tuple[float, float, float, float],
    output_name: str,
) -> None:
    pdf_path = find_pdf(pdf_prefix)
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number - 1]
        cropped = page.crop(bbox)
        image = cropped.to_image(resolution=320, antialias=True)
        output_path = OUTPUT_DIR / output_name
        image.save(output_path, format="PNG")
        print(
            f"wrote={output_path} source={pdf_path.name} "
            f"page={page_number} bbox={bbox}"
        )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    export_crop(
        "U-KAN Makes Strong Backbone",
        3,
        (100, 50, 510, 305),
        "ukan_framework_from_original_paper.png",
    )
    export_crop(
        "KC-UNet",
        2,
        (55, 55, 520, 305),
        "kc_unet_architecture_from_paper.png",
    )
    export_crop(
        "KC-UNet",
        3,
        (298, 50, 535, 165),
        "cbam_module_from_kcunet_paper.png",
    )
    export_crop(
        "U-KAN Makes Strong Backbone",
        6,
        (330, 275, 555, 420),
        "ukan_channel_activation_from_paper.png",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
