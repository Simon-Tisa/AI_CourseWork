from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SCREENSHOT_DIR = WORKSPACE / "课程论文要求" / "图片"
OUT_DIR = ROOT / "paper" / "figures"
MATLAB_OUT_DIR = ROOT / "matlab_figures" / "output"


SOURCE_IMAGES = {
    "busi_train": SCREENSHOT_DIR / "busi_ukan代码最终过程.png",
    "cvc_train": SCREENSHOT_DIR / "cvc_ukan代码运行最终过程-epoch100.png",
    "evaluate": SCREENSHOT_DIR / "mess" / "生成 metrics.csv 和预测 mask.png",
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


FONT_TITLE = font(58, bold=True)
FONT_PANEL = font(34, bold=True)
FONT_SMALL = font(24)
FONT_SMALL_BOLD = font(24, bold=True)
FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", size=24) if Path("C:/Windows/Fonts/consola.ttf").exists() else font(24)


def fit_image(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / image.width, max_h / image.height)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def paste_center(base: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    px = x + (w - image.width) // 2
    py = y + (h - image.height) // 2
    base.paste(image, (px, py))


def draw_card(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    title: str,
    accent: tuple[int, int, int],
) -> tuple[int, int, int, int]:
    x, y, w, h = xy
    shadow = (214, 222, 233)
    draw.rounded_rectangle((x + 8, y + 8, x + w + 8, y + h + 8), radius=22, fill=shadow)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=(255, 255, 255), outline=(191, 203, 219), width=3)
    draw.rounded_rectangle((x, y, x + w, y + 70), radius=22, fill=(246, 249, 252), outline=(191, 203, 219), width=0)
    draw.rectangle((x, y + 48, x + w, y + 72), fill=(246, 249, 252))
    draw.rounded_rectangle((x + 26, y + 23, x + 46, y + 43), radius=10, fill=(255, 95, 87))
    draw.rounded_rectangle((x + 58, y + 23, x + 78, y + 43), radius=10, fill=(255, 189, 46))
    draw.rounded_rectangle((x + 90, y + 23, x + 110, y + 43), radius=10, fill=(39, 201, 63))
    draw.rectangle((x, y, x + 10, y + h), fill=accent)
    draw.text((x + 132, y + 18), title, font=FONT_PANEL, fill=(22, 32, 46))
    return (x + 28, y + 90, w - 56, h - 120)


def add_image_panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    title: str,
    image_path: Path,
    accent: tuple[int, int, int],
) -> None:
    content_box = draw_card(draw, rect, title, accent)
    image = Image.open(image_path).convert("RGB")
    fitted = fit_image(image, content_box[2], content_box[3])
    paste_center(canvas, fitted, content_box)


def read_metric_summary() -> tuple[str, str]:
    table = ROOT / "paper" / "tables" / "segmentation_results.csv"
    rows: dict[str, dict[str, str]] = {}
    with table.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows[row["name"]] = row

    busi = rows["busi_ukan_seed2981"]
    cvc = rows["cvc_ukan_seed2981"]
    busi_text = f"BUSI U-KAN: IoU {float(busi['iou']):.4f}, Dice {float(busi['dice']):.4f}, infer {float(busi['infer_ms_per_image']):.2f} ms/图"
    cvc_text = f"CVC U-KAN:  IoU {float(cvc['iou']):.4f}, Dice {float(cvc['dice']):.4f}, infer {float(cvc['infer_ms_per_image']):.2f} ms/图"
    return busi_text, cvc_text


def artifact_text() -> list[str]:
    busi = ROOT / "experiments" / "results" / "busi_ukan_seed2981"
    cvc = ROOT / "experiments" / "results" / "cvc_ukan_seed2981"
    expected = ["config.yml", "log.csv", "model.pth", "metrics.csv", "predictions"]
    busi_items = [name for name in expected if (busi / name).exists()]
    cvc_items = [name for name in expected if (cvc / name).exists()]
    busi_metric, cvc_metric = read_metric_summary()
    return [
        "结果产物核对",
        f"experiments/results/busi_ukan_seed2981: {', '.join(busi_items)}",
        f"experiments/results/cvc_ukan_seed2981:  {', '.join(cvc_items)}",
        "paper/tables/segmentation_results.csv 已汇总主实验指标",
        busi_metric,
        cvc_metric,
    ]


def draw_summary_strip(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=20, fill=(248, 251, 249), outline=(199, 214, 207), width=2)
    lines = artifact_text()
    draw.text((x + 28, y + 22), lines[0], font=FONT_SMALL_BOLD, fill=(24, 73, 55))
    current_y = y + 62
    for line in lines[1:]:
        draw.text((x + 28, current_y), line, font=FONT_MONO, fill=(32, 42, 54))
        current_y += 34


def draw_artifact_card(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int]) -> None:
    content_box = draw_card(draw, rect, "结果产物核对：从实验目录到论文表格", (216, 123, 31))
    x, y, w, _ = content_box
    busi_metric, cvc_metric = read_metric_summary()
    blocks = [
        ("实验目录", [
            "experiments/results/busi_ukan_seed2981",
            "experiments/results/cvc_ukan_seed2981",
        ]),
        ("关键文件", [
            "config.yml  log.csv  model.pth",
            "metrics.csv  predictions/",
        ]),
        ("论文表格", [
            "paper/tables/segmentation_results.csv",
        ]),
        ("代表性指标", [
            busi_metric,
            cvc_metric,
        ]),
    ]
    current_y = y + 4
    for heading, lines in blocks:
        draw.text((x + 4, current_y), heading, font=FONT_SMALL_BOLD, fill=(113, 63, 18))
        current_y += 36
        for line in lines:
            draw.text((x + 22, current_y), line, font=FONT_SMALL, fill=(34, 45, 59))
            current_y += 34
        current_y += 18


def main() -> None:
    for image_path in SOURCE_IMAGES.values():
        if not image_path.exists():
            raise FileNotFoundError(image_path)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MATLAB_OUT_DIR.mkdir(parents=True, exist_ok=True)

    width, height = 3000, 1900
    canvas = Image.new("RGB", (width, height), (244, 247, 250))
    draw = ImageDraw.Draw(canvas)

    title = "真实终端运行记录：训练、评估与预测文件生成"
    title_w = draw.textbbox((0, 0), title, font=FONT_TITLE)[2]
    draw.text(((width - title_w) // 2, 46), title, font=FONT_TITLE, fill=(20, 29, 42))

    add_image_panel(
        canvas,
        draw,
        (120, 150, 1320, 650),
        "BUSI U-KAN：训练后段与 best checkpoint 保存",
        SOURCE_IMAGES["busi_train"],
        (42, 113, 202),
    )
    add_image_panel(
        canvas,
        draw,
        (1560, 150, 1320, 650),
        "CVC-ClinicDB U-KAN：训练后段与验证指标",
        SOURCE_IMAGES["cvc_train"],
        (109, 69, 188),
    )
    add_image_panel(
        canvas,
        draw,
        (120, 870, 1860, 720),
        "统一 evaluate.py：指标输出与预测 mask 生成",
        SOURCE_IMAGES["evaluate"],
        (33, 143, 114),
    )
    draw_artifact_card(draw, (2060, 870, 820, 720))

    note = "图源说明：训练与评估区域来自作者本地 Windows / Anaconda / PyTorch 环境真实运行截图；本图仅进行裁切、拼接与版式整理，未修改终端输出内容。"
    note_w = draw.textbbox((0, 0), note, font=FONT_SMALL)[2]
    draw.text(((width - note_w) // 2, 1818), note, font=FONT_SMALL, fill=(76, 88, 103))

    out_path = OUT_DIR / "runtime_terminal_evidence_collage.png"
    matlab_copy = MATLAB_OUT_DIR / "fig22_runtime_terminal_evidence_collage.png"
    canvas.save(out_path, quality=95)
    canvas.save(matlab_copy, quality=95)
    print(f"wrote={out_path}")
    print(f"wrote={matlab_copy}")


if __name__ == "__main__":
    main()
