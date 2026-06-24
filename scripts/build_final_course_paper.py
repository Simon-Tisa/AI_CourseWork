from __future__ import annotations

import csv
import shutil
import subprocess
from zipfile import ZipFile
from pathlib import Path

import numpy as np
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
TARGET_DIR = WORKSPACE / "论文撰写"
TARGET = TARGET_DIR / "基于 U-KAN 的医学图像分割算法复现、实验诊断与注意力增强研究.docx"
BACKUP = TARGET_DIR / "基于 U-KAN 的医学图像分割算法复现、实验诊断与注意力增强研究_修改前备份.docx"
FIG_DIR = TARGET_DIR / "figures"
PROJECT_FIG_DIR = ROOT / "paper" / "figures"
REFERENCE_FIG_DIR = ROOT / "paper" / "reference_figures"
EXP_FIG_DIR = ROOT / "experiments" / "figures"
MATLAB_FIG_DIR = ROOT / "matlab_figures" / "output"
TEMPLATE_DOCX = TARGET_DIR / "template_analysis" / "final_template" / "final_template.docx"

TITLE = "基于 U-KAN 的医学图像分割算法复现、实验诊断与注意力增强研究"
GITHUB_URL = "https://github.com/Simon-Tisa/AI_CourseWork.git"

BLACK = RGBColor(0x00, 0x00, 0x00)
BLUE = BLACK
MUTED = BLACK
LIGHT_BLUE = "E7E6E6"
LIGHT_GRAY = "F2F4F7"


def set_run_font(
    run,
    size: float = 12,
    bold: bool = False,
    east_asia: str = "宋体",
    ascii_font: str = "宋体",
    color: RGBColor = BLACK,
    italic: bool = False,
) -> None:
    run.font.name = ascii_font
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), east_asia)
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), ascii_font)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), ascii_font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=100, bottom=80, end=100) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_fixed_layout(table, widths_cm: list[float]) -> None:
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")

    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    total_dxa = int(sum(widths_cm) / 2.54 * 1440)
    tbl_w.set(qn("w:w"), str(total_dxa))
    tbl_w.set(qn("w:type"), "dxa")

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width_cm in widths_cm:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(int(width_cm / 2.54 * 1440)))
        grid.append(col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            width_dxa = int(widths_cm[idx] / 2.54 * 1440)
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(width_dxa))
            tc_w.set(qn("w:type"), "dxa")
            cell.width = Cm(widths_cm[idx])


def repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def hide_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "nil")


def set_cell_bottom_border(cell, size: int = 8) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    bottom = borders.find(qn("w:bottom"))
    if bottom is None:
        bottom = OxmlElement("w:bottom")
        borders.append(bottom)
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "0")
    bottom.set(qn("w:color"), "000000")


def clear_paragraph(paragraph) -> None:
    for child in list(paragraph._p):
        paragraph._p.remove(child)


def configure_page(section) -> None:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(0.0)
    section.footer_distance = Cm(1.75)
    section.different_first_page_header_footer = False


def set_page_number_start(section, start: int) -> None:
    sect_pr = section._sectPr
    pg_num_type = sect_pr.find(qn("w:pgNumType"))
    if pg_num_type is None:
        pg_num_type = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num_type)
    pg_num_type.set(qn("w:start"), str(start))


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    set_run_font(run, 10.5)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    configure_page(section)

    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "宋体")
    normal._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "宋体")
    normal._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "宋体")
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)

    for level, size in ((1, 16), (2, 15), (3, 12)):
        style = doc.styles[f"Heading {level}"]
        style.font.name = "宋体"
        style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "宋体")
        style._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "宋体")
        style._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "宋体")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = BLACK
        style.paragraph_format.line_spacing = 1.0
        style.paragraph_format.space_before = Pt(10 if level == 1 else 8)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True

    caption = doc.styles["Caption"]
    caption.font.name = "宋体"
    caption._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "宋体")
    caption._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "宋体")
    caption._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "宋体")
    caption.font.size = Pt(10.5)
    caption.font.bold = False
    caption.font.color.rgb = BLACK
    caption.paragraph_format.line_spacing = 1.0
    caption.paragraph_format.space_before = Pt(3)
    caption.paragraph_format.space_after = Pt(6)

    clear_paragraph(section.header.paragraphs[0])
    clear_paragraph(section.footer.paragraphs[0])


def start_body_section(doc: Document) -> None:
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_page(section)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    clear_paragraph(section.header.paragraphs[0])
    clear_paragraph(section.footer.paragraphs[0])
    add_page_number(section.footer.paragraphs[0])
    set_page_number_start(section, 1)


def extract_template_logo() -> Path | None:
    out = FIG_DIR / "jnu_logo.png"
    if out.exists():
        return out
    if not TEMPLATE_DOCX.exists():
        return None
    with ZipFile(TEMPLATE_DOCX) as archive:
        media = next(
            (name for name in archive.namelist() if name.startswith("word/media/")),
            None,
        )
        if media is None:
            return None
        out.write_bytes(archive.read(media))
    return out


def add_title_page(doc: Document) -> None:
    logo = extract_template_logo()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(25)
    p.paragraph_format.space_after = Pt(28)
    if logo is not None:
        p.add_run().add_picture(str(logo), width=Cm(7.8))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(44)
    r = p.add_run("本科生课程论文")
    set_run_font(r, 26, bold=True)

    items = [
        ("论文题目", TITLE),
        ("学    院", "【待补充】"),
        ("学    系", "【待补充】"),
        ("专    业", "【待补充】"),
        ("课程名称", "人工智能"),
        ("学生姓名", "蔡雪峰"),
        ("学    号", "【待补充】"),
        ("指导教师", "【待补充】"),
    ]
    table = doc.add_table(rows=len(items), cols=2)
    hide_table_borders(table)
    set_table_fixed_layout(table, [4.0, 12.0])
    for idx, (row, (label, value)) in enumerate(zip(table.rows, items)):
        row.cells[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        row.cells[1].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p0 = row.cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r0 = p0.add_run(label + "：")
        set_run_font(r0, 18 if idx == 0 else 15, bold=True)
        p1 = row.cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(value)
        set_run_font(r1, 18 if idx == 0 else 15, bold=idx == 0)
        set_cell_bottom_border(row.cells[1])
        margin = 125 if idx == 0 else 85
        set_cell_margins(row.cells[0], top=margin, bottom=margin)
        set_cell_margins(row.cells[1], top=margin, bottom=margin)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(38)
    r = p.add_run("2026 年 6 月")
    set_run_font(r, 14, bold=True)


def add_evaluation_page(doc: Document) -> None:
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_page(section)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    clear_paragraph(section.header.paragraphs[0])
    clear_paragraph(section.footer.paragraphs[0])

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("本科生课程论文成绩评定")
    set_run_font(r, 18, bold=True)

    table = doc.add_table(rows=2, cols=1)
    table.style = "Table Grid"
    set_table_fixed_layout(table, [16.0])

    comment_row = table.rows[0]
    comment_row.height = Cm(15.8)
    comment_row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
    comment_cell = comment_row.cells[0]
    comment_cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    set_cell_margins(comment_cell, top=180, start=180, bottom=180, end=180)
    p = comment_cell.paragraphs[0]
    r = p.add_run("任课教师评语：")
    set_run_font(r, 12)

    score_row = table.rows[1]
    score_row.height = Cm(5.0)
    score_row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
    score_cell = score_row.cells[0]
    score_cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(score_cell, top=180, start=180, bottom=180, end=180)
    p = score_cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("评定分数：____________")
    set_run_font(r, 12)
    p = score_cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("任课教师签字：____________")
    set_run_font(r, 12)
    p = score_cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run("年      月      日")
    set_run_font(r, 12)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_paragraph(style=f"Heading {level}")
    p.add_run(text)


def add_body(
    doc: Document,
    text: str,
    first_indent: bool = True,
    bold_prefix: str | None = None,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    keep_with_next: bool = False,
) -> None:
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.keep_with_next = keep_with_next
    if first_indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    if bold_prefix and text.startswith(bold_prefix):
        r1 = p.add_run(bold_prefix)
        set_run_font(r1, 12, bold=True)
        r2 = p.add_run(text[len(bold_prefix) :])
        set_run_font(r2, 12)
    else:
        r = p.add_run(text)
        set_run_font(r, 12)


def add_numbered_items(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(item)
        set_run_font(r, 12)


def add_reference(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Cm(0.74)
    p.paragraph_format.first_line_indent = Cm(-0.74)
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    set_run_font(r, 10.5)


def add_formula(doc: Document, formula: str, number: str) -> None:
    table = doc.add_table(rows=1, cols=2)
    hide_table_borders(table)
    set_table_fixed_layout(table, [13.8, 2.0])
    tr_pr = table.rows[0]._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)
    p = table.cell(0, 0).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(formula)
    set_run_font(r, 11.5, east_asia="Cambria Math", ascii_font="Cambria Math")
    p2 = table.cell(0, 1).paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r2 = p2.add_run(number)
    set_run_font(r2, 11)


def add_table(
    doc: Document,
    title: str,
    headers: list[str],
    rows: list[list[str]],
    widths_cm: list[float],
    source: str,
    font_size: float = 9.5,
) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(title)
    set_run_font(r, 10.5, bold=True)

    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    set_table_fixed_layout(table, widths_cm)
    repeat_table_header(table.rows[0])
    for idx, header in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = ""
        set_cell_shading(cell, LIGHT_BLUE)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(header)
        set_run_font(r, font_size, bold=True)
    for row_values in rows:
        cells = table.add_row().cells
        for idx, value in enumerate(row_values):
            cell = cells[idx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(value))
            set_run_font(r, font_size)
    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("资料来源：" + source)
    set_run_font(r, 9, color=MUTED)


def add_figure(
    doc: Document,
    path: Path | None,
    caption: str,
    source: str,
    width_cm: float = 15.8,
    placeholder: str | None = None,
) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    if path is not None and path.exists():
        run = p.add_run()
        picture = run.add_picture(str(path), width=Cm(width_cm))
        picture._inline.docPr.set("descr", caption)
        picture._inline.docPr.set("title", caption)
    else:
        table = doc.add_table(rows=1, cols=1)
        table.style = "Table Grid"
        set_table_fixed_layout(table, [15.5])
        cell = table.cell(0, 0)
        set_cell_shading(cell, LIGHT_GRAY)
        cp = cell.paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(25)
        cp.paragraph_format.space_after = Pt(25)
        rr = cp.add_run(placeholder or "【图片占位符】")
        set_run_font(rr, 11, bold=True, color=MUTED)
    cap = doc.add_paragraph(style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.keep_with_next = False
    r = cap.add_run(f"{caption}（图片来源：{source}）")
    set_run_font(r, 10.5)


def pil_font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf" if bold else "C:/Windows/Fonts/simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def create_mask_ratio_figure() -> Path:
    out = FIG_DIR / "mask_ratio_distribution.png"
    datasets = {
        "BUSI": ROOT / "data" / "processed" / "busi" / "masks" / "0",
        "CVC-ClinicDB": ROOT / "data" / "processed" / "cvc" / "masks" / "0",
    }
    ratios: dict[str, list[float]] = {}
    for name, folder in datasets.items():
        values = []
        for path in sorted(folder.glob("*.png")):
            with Image.open(path).convert("L") as mask:
                arr = np.asarray(mask)
                values.append(float((arr >= 128).mean()))
        ratios[name] = values

    w, h = 1900, 1050
    img = Image.new("RGB", (w, h), "#fbfcfd")
    draw = ImageDraw.Draw(img)
    title_font = pil_font(42, True)
    body = pil_font(22)
    small = pil_font(18)
    title = "BUSI 与 CVC-ClinicDB 目标区域占比分布"
    tw = draw.textbbox((0, 0), title, font=title_font)[2]
    draw.text(((w - tw) / 2, 38), title, font=title_font, fill="#17212b")

    colors = [("#2563eb", "#dbeafe"), ("#059669", "#d1fae5")]
    bins = np.linspace(0, 0.5, 21)
    for idx, (name, values) in enumerate(ratios.items()):
        x0 = 110 + idx * 900
        y0 = 210
        pw, ph = 760, 620
        draw.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=20, fill="#ffffff", outline="#cbd5e1", width=3)
        counts, _ = np.histogram(values, bins=bins)
        max_count = max(int(counts.max()), 1)
        plot_left, plot_top = x0 + 80, y0 + 90
        plot_w, plot_h = pw - 130, ph - 180
        draw.line((plot_left, plot_top, plot_left, plot_top + plot_h), fill="#64748b", width=3)
        draw.line((plot_left, plot_top + plot_h, plot_left + plot_w, plot_top + plot_h), fill="#64748b", width=3)
        bar_w = plot_w / len(counts)
        for j, count in enumerate(counts):
            bh = plot_h * count / max_count
            bx1 = plot_left + j * bar_w + 2
            bx2 = plot_left + (j + 1) * bar_w - 2
            by1 = plot_top + plot_h - bh
            draw.rectangle((bx1, by1, bx2, plot_top + plot_h), fill=colors[idx][0])
        draw.text((x0 + 25, y0 + 22), name, font=pil_font(27, True), fill="#17212b")
        mean = float(np.mean(values))
        median = float(np.median(values))
        draw.text(
            (x0 + 230, y0 + 28),
            f"样本数={len(values)}  均值={mean:.4f}  中位数={median:.4f}",
            font=small,
            fill="#475569",
        )
        for tick, label in ((0, "0"), (0.1, "0.1"), (0.2, "0.2"), (0.3, "0.3"), (0.4, "0.4"), (0.5, "0.5")):
            tx = plot_left + plot_w * tick / 0.5
            draw.line((tx, plot_top + plot_h, tx, plot_top + plot_h + 8), fill="#64748b", width=2)
            draw.text((tx - 14, plot_top + plot_h + 14), label, font=small, fill="#475569")
        draw.text((x0 + 285, y0 + ph - 55), "mask 像素占整幅图像比例", font=body, fill="#334155")
    draw.text((110, 940), "统计口径：处理后二值 mask 中前景像素数 / 总像素数；横轴超过 0.5 的少量样本归入图外尾部。", font=small, fill="#475569")
    img.save(out, quality=95)
    return out


def create_git_figure() -> Path:
    out = FIG_DIR / "git_version_record.png"
    result = subprocess.run(
        ["git", "log", "--pretty=format:%h | %D | %s", "-8"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    status = subprocess.run(
        ["git", "status", "--short", "--branch"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    branch_line = next((line for line in status.stdout.splitlines() if line.startswith("##")), "")
    log_lines = []
    for line in result.stdout.splitlines():
        clean = "".join(ch if ord(ch) < 128 else "" for ch in line).strip()
        if clean:
            log_lines.append(clean)
    lines = [branch_line] + log_lines
    w, h = 1900, 980
    img = Image.new("RGB", (w, h), "#0f172a")
    draw = ImageDraw.Draw(img)
    title_font = pil_font(36, True)
    mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 25) if Path("C:/Windows/Fonts/consola.ttf").exists() else pil_font(25)
    small = pil_font(18)
    draw.text((70, 45), "Local Git Version Record", font=title_font, fill="#e2e8f0")
    draw.rounded_rectangle((65, 120, 1835, 840), radius=18, fill="#111827", outline="#334155", width=3)
    y = 155
    for idx, line in enumerate(lines):
        color = "#93c5fd" if idx == 0 else "#e5e7eb"
        draw.text((100, y), line, font=mono, fill=color)
        y += 65
    draw.text((70, 900), "图源说明：作者根据本地 Git 仓库状态和提交记录生成。", font=small, fill="#94a3b8")
    img.save(out, quality=95)
    return out


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def row_by_name(rows: list[dict[str, str]], name: str) -> dict[str, str]:
    return next(row for row in rows if row["name"] == name)


def fmt(value: str | float, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def build_document() -> Document:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    if TARGET.exists() and not BACKUP.exists():
        shutil.copy2(TARGET, BACKUP)

    git_fig = create_git_figure()

    results = read_csv(ROOT / "paper" / "tables" / "segmentation_results.csv")
    busi_names = [
        "busi_unet_seed2981",
        "busi_no_kan_seed2981",
        "busi_ukan_seed2981",
        "busi_attention_ukan_seed2981",
    ]
    cvc_names = [
        "cvc_unet_seed2981",
        "cvc_no_kan_seed2981",
        "cvc_ukan_seed2981",
        "cvc_attention_ukan_seed2981",
    ]
    labels = {
        "busi_unet_seed2981": "U-Net",
        "busi_no_kan_seed2981": "U-KAN(no-KAN)",
        "busi_ukan_seed2981": "U-KAN",
        "busi_attention_ukan_seed2981": "Attention-U-KAN",
        "cvc_unet_seed2981": "U-Net",
        "cvc_no_kan_seed2981": "U-KAN(no-KAN)",
        "cvc_ukan_seed2981": "U-KAN",
        "cvc_attention_ukan_seed2981": "Attention-U-KAN",
    }

    doc = Document()
    configure_document(doc)
    add_title_page(doc)
    start_body_section(doc)

    add_heading(doc, "1 课程论文来源说明", 1)
    add_heading(doc, "1.1 选题来源与研究方向", 2)
    add_body(
        doc,
        "本文选择《人工智能》课程论文方向（一）“复现任意人工智能算法”，最终研究对象为 Kolmogorov-Arnold Network（KAN）及其医学图像分割扩展 U-KAN，而非 kNN。U-KAN 将可学习的一维边函数引入 U 型分割网络，在保留卷积局部建模和跳跃连接空间恢复能力的同时，利用 tokenized KAN block 加强中高层特征的非线性表达，具有明确的人工智能理论基础、可复现实验入口和较完整的医学应用场景[1-3]。",
    )
    add_heading(doc, "1.2 资料与图表来源", 2)
    add_body(
        doc,
        "论文主要参考 U-KAN 原论文及官方开源项目、KAN 原论文、U-Net 原论文，以及 ResU-KAN、KC-UNet、TransUKAN 和 VMKLA-UNet 等 KAN 医学图像分割研究[1-5,11-14]。实验数据来自公开的 BUSI 乳腺超声数据集和 CVC-ClinicDB 结肠镜息肉数据集[6-7]。工程实现参考 PyTorch 与 Albumentations 的官方接口说明[9-10]。文中图像分别注明为作者自绘、原论文截图、MATLAB 读取本项目数据生成或本地真实运行截图；所有定量结果均可回溯至项目中的 CSV、日志、预测文件或模型统计，不使用大语言模型生成实验数据。",
    )
    add_heading(doc, "1.3 开源项目与本人完成的工作", 2)
    add_body(
        doc,
        "本文不是直接调用官方 checkpoint 或原样运行官方训练脚本，而是在本地重新构建课程工程。本人完成了 BUSI 多 mask 合并、CVC 图像与标注配对、二值 mask 统一、固定 train/val 划分、U-Net 与 U-KAN 系列模型实现、no-KAN 消融、Attention-U-KAN 改进、差分学习率训练、全验证集统一评估、预测 mask 保存、训练曲线与结果图生成、随机种子稳定性实验、继续训练实验、错误案例分析、README、Git 版本记录和 Word 论文生成。官方代码主要用于核对网络思想和公开实验协议。",
    )
    add_heading(doc, "1.4 大语言模型辅助说明", 2)
    add_body(
        doc,
        "论文撰写过程中使用大语言模型辅助进行资料梳理、概念解释、代码调试建议、论文结构规划、语言润色和图示排版建议。数据处理、模型代码、训练与评估命令均在本地工程中实际执行；指标由 evaluate.py 和结果 CSV 文件产生，最终实验判断、图表核对与结论由本人检查确认。大语言模型没有替代实验运行，也没有生成或篡改任何实验指标。",
    )

    add_heading(doc, "2 摘要", 1)
    add_body(
        doc,
        "医学图像分割是计算机辅助诊断、病灶定位和治疗规划中的基础任务，但超声散斑噪声、弱边界、内镜反光和目标形态变化会显著增加分割难度。针对传统 U-Net 中高层非线性表达主要依赖卷积或普通线性层的问题，U-KAN 将 Kolmogorov-Arnold Network 的可学习边函数引入 U 型网络的 tokenized 中间表征。本文在本地 PyTorch 工程中对 U-KAN 进行课程级复现，整理 BUSI 与 CVC-ClinicDB 两个公开医学分割数据集，实现 U-Net、U-KAN(no-KAN)、U-KAN 和 Attention-U-KAN 四类模型，并在统一划分和统一评价口径下开展主实验、结构消融、随机种子稳定性验证和继续训练诊断。结果表明，U-KAN 在 BUSI 上取得 IoU 0.6874、Dice 0.8147，在 CVC-ClinicDB 上取得 IoU 0.7874、Dice 0.8810，均为四组主实验中的最优结果；相较 no-KAN，U-KAN 在两个数据集上的 IoU 分别提高 0.0388 和 0.0175，说明 KANLinear 对高层非线性建模具有实际贡献。Attention-U-KAN 未稳定超过原始 U-KAN，表明简单通道—空间注意力插入并非必然有效。针对 BUSI no-KAN 曲线跳变和 CVC 训练末期最优现象，补充实验进一步证明：KAN 的优势不是单一 seed 的偶然峰值，而 CVC 与官方参考值的差距也不能简单归因于训练轮数不足。本文形成了从数据整理、模型复现、训练评估、异常诊断到 GitHub 工程管理的完整闭环。",
        first_indent=False,
    )
    add_body(
        doc,
        "关键词：医学图像分割；U-KAN；Kolmogorov-Arnold Network；BUSI；CVC-ClinicDB；消融实验；实验诊断",
        first_indent=False,
        bold_prefix="关键词：",
    )

    add_heading(doc, "3 引言", 1)
    add_heading(doc, "3.1 医学图像分割背景", 2)
    add_body(
        doc,
        "医学图像分割通过为每个像素分配类别标签，获得器官、病灶或组织的空间范围，是自动筛查、手术规划、疗效评估和辅助诊断的重要前提。与自然图像相比，医学图像往往具有标注成本高、样本规模有限、类间差异小和类内差异大的特点。BUSI 乳腺超声图像中的散斑噪声、声影和弱边界会使病灶轮廓难以辨认；CVC-ClinicDB 内镜图像中的高光、褶皱和背景纹理则容易造成息肉边界偏移[6-7]。因此，模型既要保留浅层空间细节，又要学习足够强的高层语义和非线性关系。",
    )
    add_body(
        doc,
        "从临床工作流程看，分割结果并不是孤立的图像输出。乳腺超声中的病灶轮廓可用于面积、长短径、形态规则性和边界特征计算，进而辅助良恶性判断与随访比较；结肠镜中的息肉轮廓可支持病灶检出、大小估计、切除范围规划和术后质量控制。像素级误差因此具有明确含义：漏分割可能低估病灶范围，过分割则可能把正常组织纳入目标。单纯追求总体准确率会被大量背景像素主导，必须采用 IoU、Dice、Precision 和 Recall 等前景敏感指标进行综合判断[15]。",
    )
    add_body(
        doc,
        "医学分割还具有“小数据、强先验、重可靠性”的特点。公开数据集通常只有数百至数千张图像，与自然图像大规模训练条件存在明显差距；成像设备、操作者、患者人群和采集协议的变化又会带来域偏移。模型不仅要在固定验证集上获得较高分数，还应说明数据如何整理、训练如何复现、结果是否依赖偶然随机种子以及失败样本集中在哪些场景。基于这一认识，本文把工程可复现性和实验诊断与模型精度置于同等重要的位置。",
    )
    add_heading(doc, "3.2 从 U-Net 到 U-KAN 的研究动机", 2)
    add_body(
        doc,
        "U-Net 通过对称的编码器—解码器和 skip connection 将上下文建模与精确定位结合起来，是医学图像分割最具代表性的基础架构之一[3]。然而，传统卷积的感受野和普通 MLP 的固定节点激活仍可能限制复杂非线性模式的表达。KAN 受 Kolmogorov-Arnold 表示思想启发，把可学习的一维函数放在连接边上，使单条连接不再只是一个标量权重[2]。U-KAN 进一步把 KAN layer 用于 tokenized 高层表征，在卷积局部建模和 U 型空间恢复框架之间引入新的非线性映射机制[1]。",
    )
    add_body(
        doc,
        "近年的 ResU-KAN、KC-UNet、TransUKAN 和 VMKLA-UNet 分别从残差注意力、多尺度上下文、KAN-Transformer 混合和状态空间模型等角度扩展了 KAN 医学分割框架[11-14]。这些工作普遍采用多模型对比、消融实验、参数量/推理效率和定性可视化来证明模块贡献。本文据此将实验组织为“经典基线—结构消融—主复现—改进尝试—异常诊断”的完整链条，而不是只报告一个模型的单次结果。",
    )
    add_body(
        doc,
        "相关论文的实验组织提供了三个直接启示。第一，主模型必须与经典卷积基线和结构消融模型放在同一协议下比较，否则无法判断提升究竟来自新模块、网络宽度还是训练设置。第二，医学分割论文通常同时报告重叠指标、参数量、计算开销和可视化结果，因为单一数字不能完整描述临床边界质量。第三，当新增模块没有达到预期时，应将其作为负结果分析，而不是删去实验。本文保留 Attention-U-KAN 的全部结果，正是为了区分“提出改进”与“证明改进有效”这两个不同命题。",
    )
    add_body(
        doc,
        "选择 U-KAN 作为课程复现对象还考虑了任务难度与可解释的控制变量。若只运行官方代码并复述论文结论，课程实践价值有限；若重新实现整个复杂生成框架，又会超出单卡算力与课程周期。U-KAN 的公开结构既包含 KANLinear、token 化和 U 型解码等人工智能算法要点，又允许通过 no-KAN 直接替换模块，适合构造严谨消融。两个不同模态的数据集则使结论不局限于单一超声场景。",
    )
    add_figure(
        doc,
        REFERENCE_FIG_DIR / "kc_unet_architecture_from_paper.png",
        "图 1 KC-UNet 中 KAN、U 型结构与 CBAM 的组合示例",
        "引自 KC-UNet 原论文 Figure 1[12]；用于说明 KAN 医学分割后续工作的典型结构组织",
        15.8,
    )
    add_heading(doc, "3.3 本文主要工作", 2)
    add_numbered_items(
        doc,
        [
            "对 BUSI 与 CVC-ClinicDB 进行二次整理和统一格式化，生成固定 train/val 划分、数据统计和样本图。",
            "实现 U-Net、U-KAN(no-KAN) 与 U-KAN 三组核心对照，其中 no-KAN 保留 U-KAN 主体拓扑，仅将 KANLinear 替换为普通 Linear。",
            "设计 Attention-U-KAN，在四个 skip fusion 位置加入通道—空间注意力，检验注意力是否能够增强病灶区域表达。",
            "构建统一训练与评估流程，在完整验证集上累积 TP、FP、FN、TN，计算 IoU、Dice、Precision、Recall、Specificity、参数量和推理时间。",
            "针对 BUSI no-KAN 指标局部跳变和 CVC 最优 epoch 靠后的现象，补做 seed 6142 稳定性实验与 best checkpoint 继续训练实验。",
            "完成训练日志、预测 mask、论文图表、README、质量验收文档和 Git 版本记录，覆盖课程核心要求与加分项。",
        ],
    )
    add_heading(doc, "3.4 研究问题与验证假设", 2)
    add_body(
        doc,
        "本文将研究目标具体化为四个问题。问题一：在统一数据划分和训练协议下，U-KAN 是否能够超过经典 U-Net？问题二：保持 U-KAN 主体拓扑不变时，KANLinear 是否比普通 Linear 带来一致收益？问题三：在 skip fusion 后加入通道—空间注意力，是否能够进一步改善弱边界目标？问题四：训练曲线中的局部跳变和末期最优究竟代表有效学习、随机偶然还是尚未收敛？四个问题分别由 U-Net 对照、no-KAN 消融、Attention-U-KAN 对照、随机种子与继续训练补实验回答。",
    )
    add_body(
        doc,
        "据此提出可检验假设：H1，U-KAN 在 BUSI 与 CVC 上的 IoU/Dice 不低于 U-Net；H2，U-KAN 相较 no-KAN 的提升在不同数据集和补充 seed 中方向一致；H3，注意力模块可能提高对病灶区域的聚焦能力，但若过度抑制低响应边界，也可能表现为 Precision 上升而 Recall 下降；H4，若 CVC 的主要问题只是训练轮数不足，则从最佳 checkpoint 继续训练应获得超过原始最优值的结果。后文不以主观印象判断假设，而以表格、曲线和补充实验逐项检验。",
    )

    add_heading(doc, "4 算法原理与模型结构", 1)
    add_heading(doc, "4.1 U-Net 基本结构", 2)
    add_body(
        doc,
        "项目中的 U-Net 采用四级下采样和四级上采样。初始通道数为 32，编码通道依次为 32、64、128、256 和 512；每个 DoubleConv 由两层 3×3 Conv、BatchNorm 和 ReLU 组成。解码阶段使用 2×2 转置卷积上采样，并与对应编码阶段特征拼接，再通过 DoubleConv 融合。最后使用 1×1 卷积输出单通道 mask logit。该实现遵循经典 U-Net 的对称编码器—解码器与跳跃连接思想[3]，作为 CNN 基线用于判断 U-KAN 系列带来的精度收益和效率代价。",
    )
    add_body(
        doc,
        "U-Net 的核心并不只是网络外形呈字母 U，而是多尺度语义与定位信息的协同。编码器连续下采样扩大有效感受野，使深层特征逐渐聚合病灶整体形态；解码器逐级上采样恢复空间尺寸；同尺度跳跃连接将浅层纹理、边缘和位置信息直接传递到解码端，缓解下采样导致的细节损失。本文实现采用拼接而非相加融合，因此解码卷积同时接收上采样语义特征和编码器细节特征。",
    )
    add_body(
        doc,
        "将 U-Net 设为基线有两层意义。算法层面，它代表成熟的纯卷积分割范式，可检验 KAN/tokenized 模块是否真正改善区域重叠；工程层面，PyTorch 对标准卷积具有高度优化，能够提供推理速度参照。若 U-KAN 只提高极少精度却显著增加时延，则实际应用价值需要重新评估。本文不使用自绘 U-Net 架构图，而通过上述结构参数、代码路径和最终效率表描述该基线，避免图示质量影响论文表达。",
    )

    add_heading(doc, "4.2 KAN 与 KANLinear", 2)
    add_body(
        doc,
        "KAN 的理论动机来自 Kolmogorov-Arnold 表示思想：定义在有界区域上的多元连续函数，可以由有限个一维连续函数的复合与求和表示[2]。对 n 维输入 x=(x₁,…,xₙ)，其典型表达为：",
    )
    add_formula(
        doc,
        "f(x₁,…,xₙ) = Σq₌₁²ⁿ⁺¹ Φq(Σp₌₁ⁿ φq,p(xp))",
        "（4-1）",
    )
    add_body(
        doc,
        "其中，φq,p 为作用于单个输入分量的一维内部函数，Φq 为外部函数。该定理并不直接给出可训练网络，但启发 KAN 将普通神经网络连接上的标量权重替换为可学习的一维边函数。与固定激活的 MLP 相比，KAN 的非线性不只发生在节点上，而是分布在输入—输出连接本身。",
    )
    add_body(
        doc,
        "项目使用 B-spline 参数化边函数。给定非递减节点序列 {ti}，零阶基函数首先定义局部区间指示函数：",
    )
    add_formula(
        doc,
        "Bi,0(x) = 1，ti ≤ x < ti+1；否则 Bi,0(x) = 0",
        "（4-2）",
    )
    add_body(
        doc,
        "更高阶 B-spline 通过 Cox-de Boor 递推获得。令 αᵢ,ᵣ(x)=(x−tᵢ)/(tᵢ₊ᵣ−tᵢ)，则 r 阶基函数可紧凑写为：",
        keep_with_next=True,
    )
    add_formula(
        doc,
        "Bᵢ,ᵣ(x) = αᵢ,ᵣ(x)Bᵢ,ᵣ₋₁(x) + [1−αᵢ₊₁,ᵣ(x)]Bᵢ₊₁,ᵣ₋₁(x)",
        "（4-3）",
    )
    add_body(
        doc,
        "递推式说明每个高阶基函数只由相邻低阶基函数组合而成，因此具有局部支撑和分段平滑性质。本文使用 spline_order=3，即三阶 B-spline；当输入只跨越少量网格区间时，仅有邻近基函数产生非零响应，这使边函数能够局部调整而不必整体改变。",
    )
    add_body(
        doc,
        "普通 MLP 通常在节点上使用 ReLU、GELU 或 SiLU 等固定激活函数，并通过标量权重组合输入。项目中的 KANLinear 包含 base 分支和 spline 分支：base 分支对输入应用 SiLU 后进行线性变换；spline 分支将输入展开为 B-spline 基函数并使用可学习系数加权。第 j 个输出可写为：",
    )
    add_formula(
        doc,
        "yⱼ = Σᵢ [ wᵇⱼᵢ · SiLU(xᵢ) + Σₖ wˢⱼᵢₖ · Bₖ(xᵢ) ]",
        "（4-4）",
    )
    add_body(
        doc,
        "其中，Bₖ(·) 为第 k 个 B-spline 基函数，wᵇ 和 wˢ 分别为基础线性分支与样条分支的可学习权重。项目设置 grid_size=5、spline_order=3、grid_range=[-1,1]、grid_eps=0.02，并为 spline 分支保留独立尺度参数。该实现还支持根据输入分布更新 spline 网格以及计算激活/熵形式的正则项，但本课程主训练流程未额外调用动态网格更新和 KAN 正则损失。",
    )
    add_body(
        doc,
        "B-spline 具有局部支撑性质，输入落在某一区间时只激活相邻少量基函数，因此可以用分段平滑方式逼近复杂一维关系。三阶样条兼顾连续性与表达能力，五个网格则控制模型容量。网格过少会限制函数形状，网格过多会增加参数和小数据过拟合风险。base 分支保留 SiLU 线性映射，使网络即使在样条学习尚未稳定时也有一条常规梯度通路；spline 分支负责对局部非线性进行细化。两者相加比完全依赖样条更适合端到端深度网络训练。",
    )
    add_body(
        doc,
        "KAN 与 MLP 的差异不能简单概括为“把激活函数换成样条”。MLP 的可学习对象主要是节点之间的标量权重，固定激活作用于节点；KAN 的边函数本身可学习，参数沿输入维、输出维和样条基函数三个维度组织。其代价是前向计算、参数访问和内存布局更复杂，未必能像矩阵乘法和卷积那样充分利用 GPU。本文同时报告参数量和推理时间，就是为了避免把较少参数等同于较低计算成本。",
    )
    add_figure(doc, PROJECT_FIG_DIR / "kan_vs_mlp_diagram.png", "图 2 MLP 与 KAN 建模方式对比", "作者根据 KAN 原论文和个人 PPT 手绘图整理绘制", 15.8)

    add_heading(doc, "4.3 U-KAN 网络结构", 2)
    add_body(
        doc,
        "本文复现的 U-KAN 输入为三通道图像，输出为单通道二分类 mask logit，默认 embed_dims=[128,160,256]。编码器前三级为卷积阶段，通道数依次从 3 映射到 16、32 和 128，每级包含两层 3×3 Conv、BatchNorm 与 ReLU，并通过 2×2 max pooling 下采样。随后，PatchEmbed 使用 3×3 卷积和 stride=2 将 128 通道特征映射为 160 维 token，再将 160 维映射到 256 维 token。结构核对以 U-KAN 原论文和官方 PyTorch 项目为依据[1,8]。",
    )
    add_body(
        doc,
        "若输入特征为 X∈Rᴮˣᶜˣᴴˣᵂ，PatchEmbed 先用卷积完成通道投影和下采样，再展平空间维并转置为 token 序列：",
    )
    add_formula(
        doc,
        "T = LN(Flatten(Convk=3,s=2(X))ᵀ)，T ∈ Rᴮˣ⁽ᴴ′ᵂ′⁾ˣᶜ′",
        "（4-5）",
    )
    add_body(
        doc,
        "其中，H′、W′ 为卷积后的空间尺寸，C′ 为嵌入维数，序列长度 N=H′W′。该变换不把图像切成互不重叠的刚性块，而是通过带 padding 的卷积生成重叠局部表示，再由 LayerNorm 统一 token 特征尺度。",
    )
    add_body(
        doc,
        "每个 KANBlock 由 LayerNorm、KANLayer、DropPath 和 residual connection 组成。KANLayer 内含 fc1、fc2、fc3 三个 KANLinear，每个映射后接 depthwise 3×3 convolution、BatchNorm 和 ReLU，使 token 非线性映射重新获得局部空间归纳偏置。解码器首先将 256 通道特征恢复到 160 通道并与 skip4 相加，经过解码 KANBlock 后再恢复至 128 通道；后续逐级恢复为 32、16 通道，并与 skip3、skip2、skip1 融合，最终通过 1×1 卷积输出分割结果。",
    )
    add_body(
        doc,
        "第 l 个 KANBlock 的残差更新与项目 forward 实现一致，可写为：",
    )
    add_formula(
        doc,
        "Tˡ⁺¹ = Tˡ + DropPath(KANLayer(LN(Tˡ)))",
        "（4-6）",
    )
    add_body(
        doc,
        "LayerNorm 先稳定 token 通道分布，KANLayer 完成非线性映射和 depthwise 局部建模，DropPath 在训练阶段对残差分支进行随机深度正则化；恒等捷径则保留原始特征并改善深层梯度传播。当前配置的 drop_path_rate 较小，因此该式主要体现残差结构，而非强随机正则。",
    )
    add_body(
        doc,
        "从张量流看，卷积编码阶段保留二维特征布局；进入 PatchEmbed 后，特征先由卷积完成降采样和通道投影，再展平为长度 H×W 的 token 序列并转置为“批次×token×通道”。KANBlock 对每个空间 token 的通道表示进行非线性变换，随后 depthwise convolution 又将 token 恢复为空间排列以建模邻域关系。该过程在全连接表达与局部空间先验之间往返，避免只用逐 token 映射而忽视医学边界的连续性。",
    )
    add_body(
        doc,
        "解码端采用逐级双线性插值与卷积恢复分辨率，并通过相加方式融合对应尺度特征。相较 U-Net 的拼接，相加不会增加融合后的通道数，对显存更友好，但要求编码和解码特征具有相同通道数。项目在每个阶段显式设置 256→160→128→32→16 的投影，保证 skip tensor 对齐。最终输出保持 logit 形式，训练时直接交给 BCEWithLogitsLoss，评估时再执行 sigmoid，避免训练阶段重复数值变换。",
    )
    add_figure(
        doc,
        REFERENCE_FIG_DIR / "ukan_framework_from_original_paper.png",
        "图 3 U-KAN 总体结构、Tokenized KAN Block 与 KAN Layer",
        "引自 U-KAN 原论文 Figure 1[1]，由本地论文 PDF 原图裁切",
        16.0,
    )

    add_heading(doc, "4.4 U-KAN(no-KAN) 消融模型", 2)
    add_body(
        doc,
        "U-KAN(no-KAN) 不是 U-Net，而是用于隔离 KAN 机制贡献的结构消融模型。它保留 U-KAN 的卷积编码器、PatchEmbed、token 处理形式、残差块、解码路径和 skip fusion，仅在 KANLayer 中令 linear_cls=nn.Linear，将 fc1、fc2、fc3 从 KANLinear 替换为普通 Linear。因此，U-KAN 与 no-KAN 的指标差异更接近对 KANLinear 本身贡献的控制变量分析。",
    )
    add_body(
        doc,
        "该设计避免了常见的错误比较：若直接把 U-KAN 与 U-Net 的差值全部归因于 KAN，就会混入通道数、token 化、解码融合和参数规模等多项变化。no-KAN 与 U-KAN 共用相同数据流，只替换核心映射层，因此更接近单变量实验。与此同时，no-KAN 仍需执行 token 展平、三层线性映射、depthwise convolution 和 U-KAN 解码，故其推理速度不会自动等同于 U-Net，这一点在效率实验中得到验证。",
    )

    add_heading(doc, "4.5 Attention-U-KAN 改进模型", 2)
    add_body(
        doc,
        "通道—空间串联注意力的基本思想与 CBAM 相近：先根据全局平均池化和最大池化估计通道重要性，再在通道重标定后的特征上计算空间注意力[4]。图 4 给出 KC-UNet 论文采用的 CBAM 结构[12]，可作为本文改进模块的经典机制参照；本文并未照搬其完整网络，而是在 U-KAN 的四个 skip fusion 后实现轻量化 ChannelSpatialAttention。",
    )
    add_figure(
        doc,
        REFERENCE_FIG_DIR / "cbam_module_from_kcunet_paper.png",
        "图 4 CBAM 的通道注意力与空间注意力串联结构",
        "引自 KC-UNet 原论文 Figure 2[12]；该图用于解释经典注意力机制，不代表本文实现结构完全相同",
        13.8,
    )
    add_body(
        doc,
        "Attention-U-KAN 继承 U-KAN 主体结构，在四个 skip fusion 后加入 ChannelSpatialAttention。通道注意力首先使用 AdaptiveAvgPool2d 将空间信息压缩到 1×1，再通过两层 1×1 Conv、ReLU 和 Sigmoid 生成通道权重；空间注意力则对通道维求平均图和最大图，将二者拼接后使用 7×7 Conv 与 Sigmoid 生成空间权重。模块依次对融合特征进行通道和空间重标定，目标是在弱边界和背景噪声条件下突出病灶区域。需要强调的是，该结构是一项待实验检验的改进假设，而不是预设有效的结论。",
    )
    add_body(
        doc,
        "设融合特征 F∈Rᴮˣᶜˣᴴˣᵂ。与标准 CBAM 的平均池化和最大池化双通道分支不同，本项目通道注意力代码只使用全局平均池化，再经过两层 1×1 卷积生成通道权重：",
    )
    add_formula(
        doc,
        "Mc(F) = σ(W₂·ReLU(W₁·GAP(F)))，Fc = Mc(F) ⊙ F",
        "（4-7）",
    )
    add_body(
        doc,
        "其中 W₁ 将通道数压缩到 max(C/16,4)，W₂ 恢复到 C，σ 为 Sigmoid，⊙ 表示逐元素广播乘法。GAP 将每个通道压缩为一个统计量，因此 Mc 描述“哪些特征通道更重要”。",
    )
    add_body(
        doc,
        "空间注意力在通道重标定结果 Fc 上分别计算通道平均图和最大图，并沿通道维拼接：",
    )
    add_formula(
        doc,
        "Ms(Fc) = σ(Conv7×7([Avgc(Fc); Maxc(Fc)]))，F′ = Ms(Fc) ⊙ Fc",
        "（4-8）",
    )
    add_body(
        doc,
        "Avgc 和 Maxc 输出两个 B×1×H×W 空间描述图，7×7 卷积利用较大局部邻域估计病灶位置权重。最终输出 F′ 同时接受通道和空间两次乘法重标定，这也解释了为什么弱响应边界可能在连续抑制后难以恢复。",
    )
    add_body(
        doc,
        "在第 l 个解码尺度，项目先将上采样解码特征 Dl 与同尺度编码特征 El 相加，再调用注意力模块 Al；因此 Attention-U-KAN 的 skip fusion 可概括为：",
    )
    add_formula(
        doc,
        "Sl = Al(Dl + El)，l ∈ {1,2,3,4}",
        "（4-9）",
    )
    add_body(
        doc,
        "四个注意力模块分别作用于不同分辨率和通道数的融合特征。高层模块更偏向选择语义通道，低层模块更直接影响边缘与纹理。连续使用四处注意力的优点是覆盖完整解码路径，缺点是每一级 Sigmoid 权重都可能压低弱响应像素；当真实边界本身对比度很低时，被抑制的信息难以在后续阶段恢复。由此可以预期，注意力可能减少背景误检、提高 Precision，也可能造成轮廓收缩、降低 Recall。该机制分析为后文负结果提供了可解释依据。",
    )
    add_body(
        doc,
        "参数统计显示 Attention-U-KAN 仅比 U-KAN 增加 6024 个参数，说明性能变化并非来自大幅扩容。但参数增量小不等于优化容易：新增权重改变了特征幅值和梯度分配，原本为 U-KAN 设置的学习率、正则化和训练轮数未必仍是最优。为了保持对照公平，主实验没有为注意力模型单独调参，因此本文结论针对统一协议下的直接插入方案，而不是否定所有注意力与 U-KAN 的组合。",
    )
    add_figure(doc, PROJECT_FIG_DIR / "attention_ukan_module.png", "图 5 本文 Attention-U-KAN 通道—空间注意力模块", "作者根据 attention.py 与 attention_ukan.py 自行绘制，为本文改进结构", 15.8)
    add_heading(doc, "4.6 四类模型的结构关系", 2)
    add_body(
        doc,
        "四类模型形成由宽到窄的证据层次。U-Net 与 U-KAN 比较的是两种完整分割范式，能够回答最终性能和效率差异，但包含多处结构变化；no-KAN 与 U-KAN 共享 U-KAN 拓扑，只改变 KANLinear，提供最接近控制变量的算法消融；Attention-U-KAN 与 U-KAN 只增加 skip 后的重标定模块，用于检验改进假设。因此，论文解释结果时优先使用 U-KAN/no-KAN 判断 KAN 贡献，再使用 U-Net 判断相对经典基线的综合价值，最后使用 Attention-U-KAN 讨论新增模块是否互补。",
    )
    add_body(
        doc,
        "四类模型的特征融合方式也不同。U-Net 通过通道拼接保留编码器与解码器的独立信息，再用卷积学习融合；U-KAN 系列通过同通道相加获得更紧凑的融合表示。no-KAN 虽去掉样条边函数，仍保留后一种融合和 token 化；Attention-U-KAN 则在相加后进一步乘以通道与空间权重。这些差异决定了实验不能只看模型名称，而要结合具体数据流理解其 Precision、Recall 和时延表现。",
    )
    add_body(
        doc,
        "从归纳偏置角度，U-Net 强调卷积局部性和多尺度空间恢复，U-KAN 在高层加入可学习边函数以增强通道非线性，Attention-U-KAN 再引入选择性重标定。三种机制并非简单替代关系：局部卷积适合连续边界，KANLinear 适合复杂非线性映射，注意力负责动态强调特征。理想组合需要三者功能互补；若作用重叠或优化冲突，增加模块反而可能降低性能。本文实验正是对这种互补性进行实际检验。",
    )

    add_heading(doc, "5 实验设计与应用场景", 1)
    add_heading(doc, "5.1 数据集介绍", 2)
    add_body(
        doc,
        "BUSI 面向乳腺超声病灶分割，共整理得到 780 张图像[6]。其宽度范围为 190～1048 像素，高度范围为 310～719 像素，平均前景 mask 占比为 0.0783。CVC-ClinicDB 面向结肠镜息肉分割，共 612 张 384×288 图像[7]，平均 mask 占比为 0.0930。BUSI 的难点主要是散斑噪声、声影、弱边界和多标注；CVC 的难点则包括高光、褶皱和息肉边界与背景相近。",
    )
    add_body(
        doc,
        "BUSI 图像来自不同患者和病灶类型，原始分辨率跨度较大。超声成像依靠声波回波形成灰度纹理，散斑并非普通独立噪声，而会与组织结构共同出现；病灶后方声影、边缘回声衰减和设备增益差异都会改变局部对比度。部分样本具有多个标注文件，若只读取第一个 mask，会遗漏标注区域并造成训练标签不一致。因此，本项目在进入模型训练前先完成多 mask 合并和样本级核对。",
    )
    add_body(
        doc,
        "CVC-ClinicDB 的图像分辨率统一，但息肉在视野中的尺度、形状、颜色和成像距离变化明显。内镜镜头产生的高亮反射可能与病灶内部纹理相似，肠壁褶皱又可能形成近似轮廓。与 BUSI 相比，CVC 的平均前景比例略高，标准 U-Net 已能获得较强结果，因此更适合检验新模块在强基线条件下是否仍有边际收益。两个数据集共同构成“低对比超声”和“复杂彩色内镜”两种应用场景。",
    )
    add_table(
        doc,
        "表 1 数据集基本统计",
        ["数据集", "任务", "图像数", "尺寸范围", "平均 mask 占比", "训练/验证", "主要难点"],
        [
            ["BUSI", "乳腺超声病灶分割", "780", "宽 190～1048\n高 310～719", "0.0783", "624 / 156", "噪声、弱边界、多 mask"],
            ["CVC-ClinicDB", "结肠镜息肉分割", "612", "384×288", "0.0930", "490 / 122", "反光、褶皱、边界偏移"],
        ],
        [1.7, 2.5, 1.2, 2.2, 1.7, 1.8, 4.7],
        "作者根据 dataset_report.py、处理后数据目录与固定 split 文件统计",
        8.8,
    )
    add_figure(
        doc,
        MATLAB_FIG_DIR / "fig01_dataset_samples_matlab.png",
        "图 6 BUSI 与 CVC-ClinicDB 代表性样本及专家轮廓",
        "MATLAB 读取固定验证集后，按 mask 面积四分位自动选取样本并绘制轮廓；样本清单见 fig01_selected_samples.csv",
        15.8,
    )

    add_heading(doc, "5.2 数据预处理与数据工程", 2)
    add_body(
        doc,
        "原始数据统一存放在 data/raw，处理后数据存放在 data/processed。BUSI 的同一图像可能对应多个 mask，prepare_busi.py 将多个 mask 取并集并统一保存为单通道二值标注；prepare_cvc.py 完成 CVC 原图与 Ground Truth 的规范配对。SegmentationDataset 使用 OpenCV 读取三通道图像和灰度 mask，将图像归一化到 [0,1]，并把 mask 以 0.5 为阈值二值化。训练和验证阶段最终均缩放到 256×256。",
    )
    add_body(
        doc,
        "数据整理脚本采用确定性的文件匹配规则：先枚举原图，再根据文件名查找对应标注，缺失配对时立即报告，而不是静默跳过。处理后的 images 与 masks 使用同名文件，使数据集类可以通过样本 ID 完成一一对应。BUSI 多 mask 采用像素并集，是因为多个文件通常表示同一原图上的不同病灶或标注区域；并集可以保留全部阳性像素。所有 mask 在保存前统一为 0/255，读取后再映射为 0/1，避免灰度插值或压缩值造成非二值标签。",
    )
    add_body(
        doc,
        "固定划分文件由 make_splits.py 根据 seed 生成，而不是在每次训练时临时随机切分。主实验 seed2981 下 BUSI 为 624/156，CVC 为 490/122；所有模型读取同一 train.txt 与 val.txt。这样可以保证模型之间的差值不受验证样本变化干扰。补充 seed6142 实验重新生成 BUSI 划分，用于观察数据抽样与初始化变化后的趋势，而不是把新 seed 混入主表后直接比较绝对数值。",
    )
    add_body(
        doc,
        "在线增强只作用于训练集，图像和 mask 使用 Albumentations 的同一随机变换参数[10]，包含 90 度随机旋转、水平翻转和垂直翻转，每项概率为 0.5。验证集不进行随机增强，只执行尺寸统一和张量转换。对 mask 的缩放采用适合离散标签的处理逻辑，最终再次阈值化，从而避免边缘插值产生伪类别。增强范围保持适中，未加入可能改变超声灰度含义或内镜颜色分布的激进颜色扰动。",
    )
    add_table(
        doc,
        "表 2 数据预处理流程",
        ["步骤", "脚本/模块", "输入", "输出", "目的"],
        [
            ["BUSI 整理", "prepare_busi.py", "原图与一个或多个 mask", "标准 PNG 原图与合并 mask", "统一多标注样本"],
            ["CVC 整理", "prepare_cvc.py", "Original / Ground Truth", "标准 images / masks", "统一目录与文件命名"],
            ["固定划分", "make_splits.py", "处理后样本 ID", "train.txt / val.txt", "保证模型对照公平"],
            ["数据统计", "dataset_report.py", "处理后图像与 mask", "CSV 与样本图", "记录规模、尺寸和前景占比"],
            ["在线增强", "SegmentationDataset", "图像与二值 mask", "训练 Tensor", "旋转、翻转和尺寸统一"],
        ],
        [1.8, 2.8, 3.5, 3.3, 4.2],
        "作者根据项目数据处理脚本和数据集模块整理",
        8.7,
    )

    add_heading(doc, "5.3 数据可视化与统计分析", 2)
    add_body(
        doc,
        "从前景占比分布可以看到，两套数据中均存在较多小目标样本，而 BUSI 的平均前景比例更低、分布更偏向小面积区域。这意味着少量边界像素的变化就可能显著影响 IoU/Dice，也解释了 BUSI 训练曲线对阈值和随机划分较敏感。CVC 的平均前景比例略高，但高光和褶皱仍可能诱发过分割。",
    )
    add_body(
        doc,
        "前景占比低还会造成损失和指标之间的非线性关系。BCE 对所有像素逐点求和，背景像素数量远多于前景；Dice 则直接关注区域重叠。二者组合能够同时约束概率校准和前景覆盖，但训练 loss 的平滑下降并不保证阈值化 IoU 同样平滑。特别是在小病灶样本上，预测概率从 0.49 变为 0.51 对 BCE 的影响很小，却会让一批像素从背景切换为前景，造成验证指标突然变化。",
    )
    add_body(
        doc,
        "图中的长尾样本也说明均值不能代表所有难度。大病灶贡献的前景像素更多，在全局像素累计指标中权重自然更大；小病灶若完全漏检，对样本本身很严重，但在全局统计中的影响可能被稀释。因此，本文除全局指标外还保留逐图预测和典型错误案例，并在第 6.6 节进一步报告 per-image Dice 分布与按病灶面积分层结果。",
    )
    add_figure(doc, MATLAB_FIG_DIR / "fig02_mask_ratio_distribution_matlab.png", "图 7 BUSI 与 CVC-ClinicDB 的 mask 占比分布", "MATLAB 根据 data/processed 中全部 780/612 个二值 mask 统计绘制", 15.8)
    add_figure(doc, PROJECT_FIG_DIR / "experiment_workflow.png", "图 8 数据处理、实验与论文产出流程", "作者根据本项目脚本与工程目录自行绘制", 16.0)

    add_heading(doc, "5.4 实验环境", 2)
    add_table(
        doc,
        "表 3 实验环境",
        ["项目", "配置"],
        [
            ["操作系统", "Windows 11 / Windows 10 兼容环境"],
            ["Python", "3.10.18，Anaconda torch 环境"],
            ["深度学习框架", "PyTorch 2.9.1+cu126"],
            ["CUDA", "12.6"],
            ["GPU", "NVIDIA GeForce RTX 4080 Laptop GPU"],
            ["主要依赖", "torchvision、OpenCV、Albumentations、scikit-learn、Pandas、PyYAML、tensorboardX"],
            ["项目路径", str(ROOT)],
        ],
        [4.0, 11.8],
        "doctor_env.py 运行结果和本地实验环境记录",
        9.5,
    )
    add_body(
        doc,
        "环境诊断由 doctor_env.py 输出 Python 路径、依赖可用性、PyTorch/CUDA 版本、GPU 数量和设备名称。项目通过 run_python.ps1 优先调用 C:\\ProgramData\\Anaconda\\envs\\torch\\python.exe，避免 PowerShell 默认 Python 3.12 环境缺少 torch 等依赖。训练前执行 one-batch smoke test，用最小数据批验证导入路径、数据形状、前向传播、损失反向传播和 checkpoint 写入，确认无误后再启动完整实验。",
    )
    add_body(
        doc,
        "所有主实验在同一台 RTX 4080 Laptop GPU 上运行，推理时间也在同一设备和同一评估脚本中测量。由于笔记本 GPU 的功耗状态、后台进程和首次 CUDA 初始化会影响毫秒级结果，本文把时延视为工程量级比较，不宣称它是跨平台基准。参数量由可训练参数总数计算，不包含输入、激活缓存和优化器状态，因此不能直接等同于显存占用。",
    )

    add_heading(doc, "5.5 模型矩阵与训练参数", 2)
    add_table(
        doc,
        "表 4 模型矩阵",
        ["模型", "实验作用", "KANLinear", "注意力", "参数量"],
        [
            ["U-Net", "经典 CNN 分割基线", "否", "否", "7,763,041"],
            ["U-KAN(no-KAN)", "隔离 KANLinear 贡献的消融", "替换为 Linear", "否", "2,764,561"],
            ["U-KAN", "主复现模型", "是", "否", "6,356,689"],
            ["Attention-U-KAN", "注意力增强尝试", "是", "四处 skip fusion", "6,362,713"],
        ],
        [3.3, 5.3, 2.7, 2.8, 2.5],
        "作者根据模型配置与 count_parameters 统计",
        9.0,
    )
    add_table(
        doc,
        "表 5 统一训练超参数",
        ["项目", "设置", "说明"],
        [
            ["输入尺寸", "256×256", "训练和验证统一"],
            ["Batch size", "8", "所有主实验一致"],
            ["Epoch", "100", "CVC 补实验另续训 50 epoch"],
            ["优化器", "Adam", "按参数组设置学习率"],
            ["普通参数学习率", "1×10⁻⁴", "卷积、归一化、注意力等"],
            ["KAN 参数学习率", "1×10⁻²", "KANLayer 中 fc 参数"],
            ["Scheduler", "CosineAnnealingLR", "eta_min=1×10⁻⁵"],
            ["Weight decay", "1×10⁻⁴", "普通与 KAN 参数均设置"],
            ["损失函数", "0.5×BCE + DiceLoss", "兼顾像素分类与区域重叠"],
            ["数据增强", "RandomRotate90、水平/垂直翻转", "每项概率 0.5"],
            ["主 seed", "2981", "BUSI/CVC 主实验"],
            ["补充 seed", "6142", "BUSI 稳定性实验"],
        ],
        [3.8, 4.8, 7.8],
        "项目 YAML 配置、train.py 与 losses.py",
        9.1,
    )
    add_body(
        doc,
        "损失函数由 BCEWithLogitsLoss 与 soft Dice loss 组成。设 zᵢ 为模型输出 logit，pᵢ=σ(zᵢ) 为预测概率，gᵢ∈{0,1} 为二值真值，N 为像素总数。二元交叉熵刻画像素级概率误差：",
    )
    add_formula(
        doc,
        "LBCE = −(1/N)Σᵢ[gᵢlog(pᵢ) + (1−gᵢ)log(1−pᵢ)]",
        "（5-1）",
    )
    add_body(
        doc,
        "实际代码使用 BCEWithLogitsLoss 直接接收 zᵢ，以 log-sum-exp 形式完成数值稳定计算。Dice loss 则在每个样本内展平全部像素，计算 soft 区域重叠后再对 batch 求平均：",
    )
    add_formula(
        doc,
        "LDice = 1 − (1/B)Σb₌₁ᴮ (2Σᵢpbi·gbi + ε)/(Σᵢpbi + Σᵢgbi + ε)",
        "（5-2）",
    )
    add_body(
        doc,
        "其中 B 为 batch size，ε=10⁻⁵ 用于避免空前景样本出现除零。项目 losses.py 中的最终训练目标为：",
    )
    add_formula(
        doc,
        "Ltotal = 0.5·LBCE + LDice",
        "（5-3）",
    )
    add_body(
        doc,
        "该权重并不是对两项各取 0.5，而是将 BCE 乘以 0.5 后与完整 Dice loss 相加。BCE 提供逐像素概率监督，Dice 项直接优化前景区域重叠，二者结合可缓解医学图像中背景像素远多于病灶像素的问题。",
    )
    add_body(
        doc,
        "优化器采用 PyTorch Adam，学习率调度采用 CosineAnnealingLR[9]。普通卷积、归一化和注意力参数的初始学习率为 1×10⁻⁴，KANLayer 中 fc 参数使用 1×10⁻²。差分学习率的理由是样条系数和网格相关参数需要更大的更新幅度才能在有限 epoch 内形成有效边函数，而卷积特征提取器若使用同样大的学习率容易震荡。调度器在训练过程中逐步降低学习率至 1×10⁻⁵，使前期快速搜索、后期细化参数。该设置沿用项目统一配置，对四个模型保持可比较性；不含 KAN 参数的模型只使用普通参数组。",
    )
    add_body(
        doc,
        "对任一参数组，其第 t 个 epoch 的余弦退火学习率为：",
    )
    add_formula(
        doc,
        "ηt = ηmin + 0.5(ηmax−ηmin)[1 + cos(πt/Tmax)]",
        "（5-4）",
    )
    add_body(
        doc,
        "其中 Tmax=100 对应主实验训练轮数，ηmin=1×10⁻⁵；普通参数组和 KAN 参数组分别使用自己的 ηmax，但共享相同余弦退火形状。因而 KAN 参数在整个训练阶段保持更大的更新幅度，末期则共同接近较小学习率。",
    )
    add_body(
        doc,
        "训练脚本每个 epoch 记录训练 loss、验证 loss、验证 IoU 和验证 Dice，并按验证 IoU 保存 best model。选择 IoU 作为 checkpoint 标准，是因为它对 FP 和 FN 都有直接惩罚，且与 Dice 单调相关。最终论文表格不直接抄录训练日志中的 batch 指标，而统一调用 evaluate.py 加载 best checkpoint，在完整验证集上重新累积混淆矩阵。这样可以避免训练阶段平均方式与最终测试口径不一致。",
    )
    add_heading(doc, "5.6 对照实验与补充实验设计", 2)
    add_body(
        doc,
        "主实验在 BUSI 和 CVC 上分别运行 U-Net、no-KAN、U-KAN 和 Attention-U-KAN。四组模型使用同一分辨率、batch size、训练轮数、数据划分和评估脚本。U-Net 回答“U-KAN 相比经典 CNN 是否具有优势”；no-KAN 回答“收益是否来自 KANLinear”；Attention-U-KAN 回答“简单通道—空间注意力是否形成互补”。补充实验则针对训练中实际观察到的异常：BUSI seed 6142 用于检验局部峰值是否偶然；CVC best checkpoint 继续训练 50 epoch 用于判断 100 epoch 是否不足。",
    )
    add_body(
        doc,
        "公平性控制包括五个方面：数据相同，四模型使用同一 split；输入相同，均缩放至 256×256；训练预算相同，主实验均为 100 epoch、batch size 8；模型选择规则相同，均按验证 IoU 保存最佳权重；最终评价相同，均由 evaluate.py 在完整验证集上计算。模型内部参数量和计算结构可以不同，因为这正是需要被比较的对象，但不允许通过单独延长某一模型训练或更换验证集获得优势。",
    )
    add_body(
        doc,
        "补充实验遵循“问题驱动”原则，而非看到结果后无目标地增加运行。BUSI 曲线提出的是稳定性问题，因此改变随机种子并比较 U-KAN/no-KAN 的相对方向；CVC 曲线提出的是训练轮数问题，因此固定原模型和数据，从 best checkpoint 延续优化。两个实验分别改变一个关键因素，使结果能够回答原始疑问。若继续训练只产生新的末期峰值而未超过原值，就不能继续用“再多跑一些也许会更高”解释差距。",
    )
    add_heading(doc, "5.7 可复现性与质量控制", 2)
    add_body(
        doc,
        "可复现性控制贯穿数据、代码、配置和结果四个层面。数据层面，原始数据与处理后数据分离，处理脚本可重复生成统一目录，split 文件固定样本列表；代码层面，模型、损失、指标和数据集模块位于 src 包，命令行脚本只负责组装流程；配置层面，每个实验由独立 YAML 描述数据集、模型、seed 和超参数，并在实验目录中保存 config.yml 副本；结果层面，日志、最佳权重、最终指标和逐图预测共同保存。",
    )
    add_body(
        doc,
        "训练入口设置名称冲突和覆盖保护，避免误把新实验写入旧目录。需要继续训练时显式提供 resume checkpoint，并使用新的实验名称保存，保留原始基线。评估脚本根据实验目录中的配置重建模型，再加载 model.pth；若模型类型或参数不一致会在权重加载阶段暴露，而不是静默使用错误结构。预测文件以验证样本 ID 命名，能够与原图和真值一一对应。",
    )
    add_body(
        doc,
        "指标质量控制的关键是统一口径。训练过程中用于观察的 val IoU/Dice 可能受批次聚合方式影响，最终论文结果全部由独立 evaluate.py 重算。该脚本在完整验证集上累积整数混淆矩阵，并统一阈值、epsilon 和计时方式。新训练日志已改为同一全局口径，但历史模型无需重训，因为 checkpoint 本身不包含指标定义；只要所有 checkpoint 通过同一 evaluate.py 重新评估，新旧实验结果仍可直接进入同一主表。",
    )
    add_body(
        doc,
        "质量检查还包括文件级验证：汇总脚本检查必需 metrics.csv 是否存在，绘图脚本只读取机器生成日志，论文生成脚本从 CSV 填充表格而非手工录入。Word 生成后再次扫描标题、表格、图片、占位符和异常工具标记。学号、班级和指导教师属于无法从项目推断的个人信息，故仅在封面保留三个明确待补充项，其余正文不使用内容占位符。",
    )

    add_heading(doc, "6 实验结果与分析", 1)
    add_heading(doc, "6.1 评价指标与统一评估口径", 2)
    add_body(
        doc,
        "所有最终指标均由 evaluate.py 计算。脚本在完整验证集上累积像素级 TP、FP、FN、TN，预测概率经 sigmoid 后以 0.5 为阈值二值化。设 zᵢ 为 logit，则离散预测为：",
    )
    add_formula(doc, "ĝᵢ = 𝟙[σ(zᵢ) ≥ 0.5]", "（6-1）")
    add_body(
        doc,
        "ĝᵢ 与真值 gᵢ 在完整验证集的全部像素上共同决定混淆矩阵：",
    )
    add_formula(
        doc,
        "TP=Σᵢĝᵢgᵢ，FP=Σᵢĝᵢ(1−gᵢ)，\n"
        "FN=Σᵢ(1−ĝᵢ)gᵢ，TN=Σᵢ(1−ĝᵢ)(1−gᵢ)",
        "（6-2）",
    )
    add_body(
        doc,
        "GPU 推理计时前后调用 torch.cuda.synchronize，避免异步执行低估耗时。模型同时保存每张验证图像的预测 mask，并输出参数量与单图平均推理时间。基于全局混淆矩阵，评价指标定义如下：",
    )
    add_formula(doc, "IoU = TP / (TP + FP + FN)", "（6-3）")
    add_formula(doc, "Dice = 2TP / (2TP + FP + FN)", "（6-4）")
    add_formula(doc, "Precision = TP / (TP + FP)", "（6-5）")
    add_formula(doc, "Recall = TP / (TP + FN)", "（6-6）")
    add_formula(doc, "Specificity = TN / (TN + FP)", "（6-7）")
    add_formula(doc, "Dice = 2·IoU / (1 + IoU)", "（6-8）")
    add_body(
        doc,
        "IoU 与 Dice 都衡量预测前景和真实前景的重叠，两者的优化性质和排序关系已有系统理论分析[15]。式（6-8）表明，在同一混淆矩阵口径下二者是严格单调关系，因此模型按 IoU 与 Dice 排序通常一致；Dice 对重叠区域给予两倍权重，数值通常高于 IoU。Precision 反映预测为病灶的像素中有多少是真实病灶，较低时往往存在过分割；Recall 反映真实病灶像素被找回的比例，较低时表示漏分割。Specificity 主要受大量背景像素影响，在前景比例不足 10% 的数据上通常接近 1，因此必须与其他指标联合解读，不能因 Specificity 高就判断模型分割优秀。",
    )
    add_body(
        doc,
        "全局口径先在整个验证集上汇总 TP、FP、FN、TN，再计算指标；它与先逐图计算再求平均的结果并不相同。全局口径对面积较大的病灶赋予更高像素权重，数值更稳定，也与训练过程中累计混淆矩阵的实现一致。此前训练日志曾使用过不同聚合方式，后续已统一新实验日志，但论文主表全部来自 evaluate.py，因此历史 checkpoint 与新跑实验仍可在同一最终评价口径下比较。",
    )

    def result_rows(names):
        rows = []
        for name in names:
            row = row_by_name(results, name)
            rows.append(
                [
                    labels[name],
                    fmt(row["iou"]),
                    fmt(row["dice"]),
                    fmt(row["precision"]),
                    fmt(row["recall"]),
                    fmt(row["specificity"]),
                    f"{int(row['params']):,}",
                    fmt(row["infer_ms_per_image"], 2),
                ]
            )
        return rows

    add_heading(doc, "6.2 BUSI 主实验结果", 2)
    add_table(
        doc,
        "表 6 BUSI 主实验结果",
        ["模型", "IoU", "Dice", "Precision", "Recall", "Specificity", "参数量", "ms/图"],
        result_rows(busi_names),
        [3.2, 1.5, 1.5, 1.7, 1.5, 1.8, 2.4, 1.8],
        "evaluate.py 对 BUSI seed2981 验证集的统一评估结果",
        8.5,
    )
    add_body(
        doc,
        "BUSI 上 U-KAN 取得最高 IoU 0.6874 和 Dice 0.8147。相较 no-KAN，其 IoU 提高 0.0388、Dice 提高 0.0279；Recall 从 0.7356 提升到 0.8118，说明 KANLinear 的主要收益之一是减少弱边界病灶的漏分割。no-KAN 具有最高 Precision 0.8459，但 Recall 较低，表现出明显的保守预测倾向。Attention-U-KAN 的 IoU 为 0.6769，低于 U-KAN 0.0104，说明简单注意力插入没有形成稳定增益。",
    )
    add_body(
        doc,
        "与 U-Net 相比，U-KAN 的 IoU 提高 0.0505，Dice 提高 0.0365，Recall 提高 0.0799，而 Precision 略低 0.0131。该组合说明 U-KAN 倾向于输出更完整的病灶范围，增加的少量假阳性被显著减少的漏分割所抵消。对于弱边界乳腺超声，这种 Precision—Recall 平衡比单纯追求保守轮廓更合理，因为病灶边缘遗漏会直接影响面积和形态估计。",
    )
    add_body(
        doc,
        "no-KAN 的参数量只有 2.76M，却超过 U-Net 的 IoU 0.0117，说明 U-KAN 的整体 tokenized 拓扑本身也有一定价值；在此基础上加入 KANLinear 又获得 0.0388 的进一步提升。由此不能把结果简化为“参数越多越好”：U-Net 参数量 7.76M 高于 U-KAN，指标却更低；Attention-U-KAN 参数略多于 U-KAN，指标同样下降。结构归纳偏置和优化行为比单纯参数规模更关键。",
    )

    add_heading(doc, "6.3 CVC-ClinicDB 主实验结果", 2)
    add_table(
        doc,
        "表 7 CVC-ClinicDB 主实验结果",
        ["模型", "IoU", "Dice", "Precision", "Recall", "Specificity", "参数量", "ms/图"],
        result_rows(cvc_names),
        [3.2, 1.5, 1.5, 1.7, 1.5, 1.8, 2.4, 1.8],
        "evaluate.py 对 CVC seed2981 验证集的统一评估结果",
        8.5,
    )
    add_body(
        doc,
        "CVC 上 U-KAN 仍取得最优 IoU 0.7874 和 Dice 0.8810，但相对 U-Net 的提升仅为 0.0070 和 0.0044，说明 CVC 上经典 U-Net 已是较强基线。Attention-U-KAN 的 Precision 达到 0.9207，而 Recall 降至 0.8168；结合 IoU/Dice 同步下降可以判断，注意力模块抑制了部分不确定区域，却也漏掉了真实息肉边缘。",
    )
    add_body(
        doc,
        "U-KAN 相对 no-KAN 的 CVC IoU 提高 0.0175、Dice 提高 0.0110，方向与 BUSI 一致但幅度更小。CVC 中 no-KAN 的 Recall 为 0.8378，U-KAN 提升至 0.8503，同时 Precision 也从 0.9048 提升到 0.9140，表明 KANLinear 在该数据上不是通过单纯扩大预测区域换取 Recall，而是同时改善了前景覆盖与误检控制。这一结果支持 H2 的跨数据集方向一致性。",
    )
    add_body(
        doc,
        "U-Net 的 CVC Precision 达到 0.9248，为四模型最高，且推理时间仅 3.72 ms/图。若应用强调实时筛查和低误报，U-Net 仍具有很强竞争力；若优先追求最大区域重叠和召回，U-KAN 更优。模型选择因此不应只根据表中加粗的最高 IoU，而要结合临床任务对漏检、误检和时延的容忍度。",
    )
    add_figure(doc, MATLAB_FIG_DIR / "fig03_main_results_matlab.png", "图 9 两个数据集的主实验 IoU/Dice 对比", "MATLAB 直接读取 segmentation_results.csv 绘制", 15.8)
    add_figure(doc, MATLAB_FIG_DIR / "fig11_metric_heatmap_matlab.png", "图 10 主实验五项评价指标热力图", "MATLAB 直接读取 segmentation_results.csv 绘制；颜色范围统一为 0.60～1.00", 15.8)

    add_heading(doc, "6.4 训练过程与曲线诊断", 2)
    add_figure(doc, MATLAB_FIG_DIR / "fig04_busi_training_curves_matlab.png", "图 11 BUSI 四模型训练曲线", "MATLAB 直接读取四个实验目录中的 log.csv 绘制", 16.0)
    add_figure(doc, MATLAB_FIG_DIR / "fig05_cvc_training_curves_matlab.png", "图 12 CVC 四模型训练曲线", "MATLAB 直接读取四个实验目录中的 log.csv 绘制", 16.0)
    add_body(
        doc,
        "BUSI no-KAN 的 loss 曲线整体高于其他模型，但验证 IoU/Dice 在局部 epoch 出现突然跳升。该现象不能直接解释为 no-KAN 学得更好：BCE+Dice loss 在连续概率空间上优化，而 IoU/Dice 在阈值化后计算；当验证集规模较小且前景占比低时，少数边界像素跨过 0.5 阈值便可能造成明显跳变。CVC 中 U-Net 的 best epoch 靠近 99，Attention-U-KAN 也靠近训练末端，引出了“是否尚未收敛”的疑问。本文因此把异常曲线转化为两个可验证假设，而不是选择性报告峰值。",
    )
    add_body(
        doc,
        "首先分析“loss 更高但指标更好”的表面矛盾。训练 loss 是训练集在数据增强和连续概率下的平均目标，验证 IoU 是验证集在固定阈值下的区域重叠，两者的数据、聚合方式和数学目标均不同。no-KAN 的预测概率可能整体更不自信，使 BCE 较高，但部分样本的二值轮廓恰好落在合理范围；反之，某模型即使概率更平滑、loss 更低，也可能在 0.5 阈值附近漏掉边界。因此不能用一条训练 loss 曲线直接推断最终 IoU 排名。",
    )
    add_body(
        doc,
        "其次分析局部“蹦升”是否意味着模型蒙对。偶然性可能来自权重初始化、mini-batch 顺序、增强组合和验证集中少数大病灶。如果跳升只在 seed2981 出现，换 seed 后 U-KAN/no-KAN 的相对关系可能反转；若换 seed 后绝对数值变化但 U-KAN 仍领先，则更合理的解释是小数据方差较大，而非结论完全由一次峰值制造。基于这一判断，补实验没有只重跑 no-KAN，而是同时重跑 U-KAN，保证相对比较仍然受控。",
    )
    add_body(
        doc,
        "对于 CVC，best epoch 接近训练末端只能说明后期仍出现过最好值，不能单凭 epoch 编号断定未收敛。判断收敛还需观察最后若干 epoch 的改善幅度、验证曲线是否进入平台、继续训练能否突破原峰值。U-KAN 原始 best epoch 为 86，并非 99；其末段 IoU 波动很小。继续训练实验从最佳而非最后 checkpoint 出发，直接检验额外优化预算是否能够提升可用模型。",
    )
    add_figure(doc, PROJECT_FIG_DIR / "experiment_diagnosis_flow.png", "图 13 从异常曲线到补充实验的诊断流程", "作者根据训练日志观察和补充实验决策自行绘制", 16.0)

    add_heading(doc, "6.5 定性预测结果", 2)
    add_figure(doc, MATLAB_FIG_DIR / "fig06_busi_prediction_comparison_matlab.png", "图 14 BUSI 预测结果对比", "MATLAB 读取验证集原图、真值与两个模型的 predictions 生成", 14.2)
    add_figure(doc, MATLAB_FIG_DIR / "fig07_cvc_prediction_comparison_matlab.png", "图 15 CVC-ClinicDB 预测结果对比", "MATLAB 读取验证集原图、真值与两个模型的 predictions 生成", 14.2)
    add_body(
        doc,
        "定性结果显示，U-KAN 通常能够更完整地覆盖弱边界病灶和息肉区域。Attention-U-KAN 在部分样本中可以抑制背景误检，但在低对比边缘容易产生收缩，从而与其 Precision 较高、Recall 较低的定量结果一致。需要注意，单个样本只能用于解释模型行为，不能替代完整验证集上的统一指标。",
    )
    add_body(
        doc,
        "可视化按照“原图—真值—各模型预测”的固定列顺序展示，样本选择同时包含相对清晰和较困难案例，避免只挑选最成功结果。观察重点包括轮廓完整性、边缘偏移、孤立假阳性和目标内部空洞。U-KAN 的主要优势表现为轮廓连续和病灶覆盖完整；U-Net 与 no-KAN 在部分低对比边缘出现收缩；Attention-U-KAN 对显著区域聚焦较强，但并未稳定恢复模糊外缘。",
    )
    add_body(
        doc,
        "定性图与定量指标形成相互校验：若某模型 Precision 高而 Recall 低，图中应更常出现轮廓偏小和漏掉边缘；若 Recall 高而 Precision 略低，则可能有少量外扩。本文不通过肉眼判断总体优劣，而是使用图像解释表格中的误差结构。这种“指标回答多少、图像回答哪里”的组合也是医学分割论文常用的结果组织方式。",
    )

    add_heading(doc, "6.6 错误案例与失败模式分析", 2)
    add_heading(doc, "6.6.1 典型过分割与漏分割案例", 3)
    add_figure(doc, MATLAB_FIG_DIR / "fig08_error_cases_matlab.png", "图 16 U-KAN 典型过分割与漏分割案例", "MATLAB 遍历全部验证样本，分别按 FP/真值面积和 FN/真值面积自动选择代表案例；清单见 fig08_error_cases_selected.csv", 15.8)
    add_body(
        doc,
        "BUSI 中的典型失败包括极弱边界、强散斑噪声、小病灶以及多个疑似区域，模型可能只覆盖病灶中心或把高回声组织误判为病灶。CVC 中的反光和褶皱容易造成过分割，边界与背景颜色相近时则容易漏分割。这些错误说明当前模型仍受局部纹理和固定阈值影响。可行的改进包括 Boundary Loss[17]、Tversky/Focal Tversky 损失[16,18]、多尺度训练、阈值校准、形态学后处理和更合理的注意力插入位置。",
    )
    add_body(
        doc,
        "从误差叠加图看，错误并非均匀分布在目标内部，而主要集中于边界和视觉混淆区域。绿色命中区域通常覆盖病灶主体，蓝色漏分割沿低对比外缘出现，红色过分割则靠近与病灶纹理相似的背景。这说明当前网络已经学到目标级语义，但边界定位仍是瓶颈。若仅增加分类能力而不引入边界约束，模型可能继续提高内部置信度，却无法解决轮廓偏移。",
    )
    add_body(
        doc,
        "固定阈值 0.5 也可能不是每个模型和数据集的最优决策点。阈值降低通常提高 Recall、扩大预测区域，阈值升高则提高 Precision、收缩轮廓。为保证主实验公平，本文没有对各模型单独调阈值；未来可在独立校准集上绘制 Precision—Recall 曲线并选择统一规则。必须避免直接在验证集上为每个模型挑选最优阈值，否则会引入额外的验证集过拟合。",
    )
    add_heading(doc, "6.6.2 逐图性能分布与病灶面积分层", 3)
    add_figure(doc, MATLAB_FIG_DIR / "fig12_failure_distribution_size_matlab.png", "图 17 逐图 Dice 分布与病灶面积分层结果", "MATLAB 对 BUSI 156 张、CVC 122 张验证样本逐图重算 Dice，并按各数据集 mask 面积三分位划分小/中/大病灶", 16.0)
    add_body(
        doc,
        "全局 IoU/Dice 会让大病灶贡献更多像素，因此需要结合逐图分布判断模型是否只在少数大目标上表现良好。箱线图展示中位数、四分位区间和离群困难样本；面积分层图则比较四种模型在小、中、大病灶上的平均逐图 Dice。如果小病灶组明显低于大病灶组，说明模型的主要瓶颈不是整体语义识别，而是目标像素稀少、边界比例高和下采样后的信息损失。该结果比只列四个失败样本更能说明失败是否具有系统性。",
    )
    add_heading(doc, "6.6.3 FP/FN 误差构成", 3)
    add_figure(doc, MATLAB_FIG_DIR / "fig13_error_composition_matlab.png", "图 18 过分割与漏分割误差构成", "MATLAB 根据全部验证样本的 TP、FP、FN 统计绘制；左图为全局误差比例，右图为 U-KAN 逐图误差平衡", 15.8)
    add_body(
        doc,
        "将 FP 和 FN 分别除以真值前景面积，可以在不同目标大小之间比较过分割和漏分割强度。散点落在对角线上方代表漏分割主导，落在下方代表过分割主导。该分析能够直接连接 Precision/Recall：Attention-U-KAN 若在 CVC 中 FN 比例增大，就与 Recall 下降相互印证；BUSI 中若 FP 和 FN 同时存在，则说明简单注意力既没有稳定抑制背景，也没有保护弱边界。",
    )
    add_heading(doc, "6.6.4 特征图解释的证据边界", 3)
    add_figure(doc, REFERENCE_FIG_DIR / "ukan_channel_activation_from_paper.png", "图 19 U-KAN 原论文中的通道激活可解释性示例", "引自 U-KAN 原论文 Figure 4[1]；仅作为可解释性分析方法参照，不属于本文实验结果", 13.8)
    add_body(
        doc,
        "U-KAN 原论文使用通道激活热图说明 KAN 结构对病灶区域的响应，如图 19 所示。本文当前实验目录只保存二值预测 mask，没有保存 sigmoid 概率图和中间层激活，因此不把后处理得到的伪热图冒充真实特征图。若继续开展本文模型的激活分析，应重新加载 checkpoint，在卷积编码层、Tok-KAN 层和注意力层注册 forward hook，对同一输入保存特征张量，再使用统一的通道聚合和归一化规则比较 U-KAN 与 Attention-U-KAN。当前失败结论以可复核的像素误差和逐图统计为主。",
    )

    add_heading(doc, "6.7 BUSI 随机种子稳定性实验", 2)
    add_table(
        doc,
        "表 8 BUSI seed 稳定性实验",
        ["模型", "seed2981 IoU", "seed2981 Dice", "seed6142 IoU", "seed6142 Dice", "平均 IoU", "平均 Dice"],
        [
            ["U-KAN(no-KAN)", "0.6486", "0.7869", "0.5942", "0.7454", "0.6214", "0.7661"],
            ["U-KAN", "0.6874", "0.8147", "0.6157", "0.7621", "0.6515", "0.7884"],
        ],
        [3.4, 2.1, 2.1, 2.1, 2.1, 2.0, 2.0],
        "paper/tables/busi_seed_stability.csv",
        8.8,
    )
    add_body(
        doc,
        "seed6142 下两种模型的绝对指标均下降，但 U-KAN 仍优于 no-KAN；两 seed 平均后，U-KAN 的 IoU 领先 0.0301、Dice 领先 0.0223。这说明 KAN 的收益不是 seed2981 的单次幸运峰值，但 BUSI 对划分和初始化明显敏感。由于本项目只补做了两个 seed，本文不把结果表述为严格的多次统计显著性结论，而仅认为存在方向一致的稳定趋势。",
    )
    add_body(
        doc,
        "从 seed2981 到 seed6142，no-KAN 的 IoU 下降 0.0544，U-KAN 下降 0.0717，说明两模型都受到数据划分和随机训练影响，U-KAN 的绝对波动甚至更大。稳定性结论因此不是“U-KAN 波动更小”，而是“在两种随机条件下均保持相对领先”。这一表述区分了性能优势与方差大小，避免只报告两次均值后掩盖单次波动。",
    )
    add_body(
        doc,
        "若要达到更严格的论文统计要求，还应运行官方提示的第三个 seed1187，报告均值、标准差，并对同一验证协议下的逐图 Dice 进行配对检验或 bootstrap 置信区间估计。课程算力与时间限制下，本文用第二 seed 回答最直接的偶然峰值质疑，同时明确证据边界，不将两次实验包装为充分统计显著性。",
    )

    add_heading(doc, "6.8 CVC 继续训练实验", 2)
    add_table(
        doc,
        "表 9 CVC U-KAN 继续训练实验",
        ["实验", "设置", "训练轮数", "best epoch", "IoU", "Dice", "相对原始 IoU"],
        [
            ["cvc_ukan_seed2981", "从头训练", "100", "86", "0.7874", "0.8810", "0.0000"],
            ["cvc_ukan_seed2981_ft50", "best checkpoint 续训", "50", "48", "0.7847", "0.8794", "-0.0027"],
        ],
        [3.9, 3.2, 1.8, 1.8, 1.6, 1.6, 2.1],
        "paper/tables/cvc_continued_training.csv",
        8.8,
    )
    add_body(
        doc,
        "从原始 best checkpoint 继续训练 50 epoch 后，IoU 由 0.7874 变为 0.7847，没有超过原始模型。原始 CVC U-KAN 最后 10 epoch 的 val IoU 变化仅约 0.0006，也支持其已接近平台期。因此，官方参考值与本地结果的差距不能简单归因于训练不足，更可能与随机划分、预处理数据、评价实现、多 seed 平均和官方 checkpoint 等因素共同相关。",
    )
    add_body(
        doc,
        "续训模型的 best epoch 为续训阶段第 48 轮，说明额外阶段仍发生轻微波动，但峰值低于原始 0.7874。若模型真正因 100 epoch 不足而持续欠拟合，合理预期应是增加训练后越过原峰值；实际结果不支持这一假设。继续训练没有带来收益还可能与学习率调度重启方式有关，但这进一步说明“延长 epoch”不是无需条件的解决方案，必须同时明确 scheduler、优化器状态和 checkpoint 恢复策略。",
    )
    add_body(
        doc,
        "官方 CVC IoU 0.8561 与本文 0.7874 相差较大，但二者不是同一受控实验。官方 README 的训练轮数、随机种子集合、数据目录和模型权重来源与本项目课程协议存在差异。本文能确认的是本地代码在统一对照中 U-KAN 最优、额外 50 epoch 未解决差距；不能确认的部分应保留为协议差异，而不能通过反复续训直到接近公开数字。这样的结论虽然更谨慎，但比选择性追逐目标值更符合复现实验规范。",
    )
    add_figure(doc, MATLAB_FIG_DIR / "fig09_supplemental_experiments_matlab.png", "图 20 稳定性与收敛性补充实验结果", "MATLAB 直接读取 busi_seed_stability.csv 与 cvc_continued_training.csv 绘制", 15.5)

    add_heading(doc, "6.9 模型效率与工程代价", 2)
    add_table(
        doc,
        "表 10 模型参数量、推理时间与性能特点",
        ["模型", "参数量", "BUSI ms/图", "CVC ms/图", "性能特点"],
        [
            ["U-Net", "7.76M", "3.60", "3.72", "速度最快，CVC 上已是强基线"],
            ["U-KAN(no-KAN)", "2.76M", "35.22", "43.46", "参数最少，但 tokenized 结构仍较慢"],
            ["U-KAN", "6.36M", "37.15", "45.90", "两个数据集 IoU/Dice 最优"],
            ["Attention-U-KAN", "6.36M", "40.69", "44.02", "增加开销，未形成稳定增益"],
        ],
        [3.3, 2.0, 2.1, 2.1, 6.3],
        "作者根据 evaluate.py 输出整理",
        9.0,
    )
    add_body(
        doc,
        "U-Net 虽然参数量最大，但卷积实现高度优化，推理速度显著快于 U-KAN 系列。no-KAN 参数量最少却并不快，说明开销不仅来自 B-spline，还来自 token 展平、多个逐 token 映射、depthwise block 和解码路径。U-KAN 的精度提升不是免费收益；在实时超声或内镜应用中，还需要进一步研究轻量化 KAN、减少 token 阶段数量或进行算子融合。",
    )
    add_body(
        doc,
        "BUSI 上 U-KAN 约为 U-Net 推理时延的 10.3 倍，CVC 上约为 12.3 倍。两数据集输入尺寸相同，但 U-KAN 系列在 CVC 测得时延略高，可能受运行时状态和测量波动影响，因此不应把几毫秒差异解释为数据集本身导致的结构变化。更可靠的结论是：标准 U-Net 位于 4 ms/图量级，U-KAN 系列位于 35～46 ms/图量级，存在明显效率等级差异。",
    )
    add_body(
        doc,
        "从精度—效率权衡看，BUSI 中 U-KAN 的较大 IoU 增益更能补偿额外时延；CVC 中增益仅 0.0070，是否值得使用取决于部署要求。离线病例分析可以容忍几十毫秒时延，而实时视频内镜还需考虑帧率、预处理、数据传输和后处理，总延迟会高于纯模型前向时间。课程实验因此只给出模型级证据，不直接声称已经满足临床实时部署。",
    )
    add_figure(doc, MATLAB_FIG_DIR / "fig10_efficiency_tradeoff_matlab.png", "图 21 模型精度、推理时间与参数量权衡", "MATLAB 读取 segmentation_results.csv 绘制；横轴为对数时间，点大小表示参数量", 15.8)

    add_heading(doc, "6.10 代码运行与工程证据", 2)
    add_figure(doc, MATLAB_FIG_DIR / "fig14_runtime_evidence_matlab.png", "图 22 从运行命令到论文结果的可复现证据链", "MATLAB 根据项目命令入口、实验目录结构和 segmentation_results.csv 组织绘制", 15.8)
    add_body(
        doc,
        "运行记录覆盖 BUSI/CVC 主模型训练、评估指标输出、metrics.csv 与预测 mask 生成。每个实验目录保存 config.yml、log.csv、model.pth、metrics.csv 和 predictions，能够从配置追溯到最终表格。训练脚本还提供 one-batch smoke test、覆盖参数、resume checkpoint 和 overwrite 保护，降低长时间实验因配置错误或误覆盖造成的风险。",
    )
    add_body(
        doc,
        "工程证据的作用不是装饰论文，而是建立结果的可追溯链：YAML 决定模型和超参数，train.py 生成日志与 checkpoint，evaluate.py 从 checkpoint 生成 metrics.csv 和 predictions，summarize_results.py 汇总表格，绘图脚本再读取 CSV 或日志生成论文图。任何表中数字都应能沿该链条回到原始实验目录。若只保留截图而缺少配置和机器可读结果，就无法可靠复核。",
    )
    add_figure(
        doc,
        MATLAB_FIG_DIR / "fig15_runtime_screenshots_matlab.png",
        "图 23 项目训练、评估与预测生成的真实终端截图",
        "作者在本地 Windows/Anaconda/PyTorch 环境实际运行时截取；MATLAB 仅进行裁切与版式整理，未修改终端输出内容",
        15.8,
    )
    add_body(
        doc,
        "图 23 展示真实训练后段、best checkpoint 保存信息以及统一评估命令输出，满足课程对代码运行截图的要求。项目还保留运行环境诊断、固定 split、README 命令和 Git 提交历史。版本化开发过程依次覆盖工程初始化、模型和数据实现、CVC 扩展、补充实验与论文材料，使代码演进与研究思路相对应。后续提交 GitHub 时应确保大体积原始数据和临时缓存不进入仓库，同时保留可重新下载数据、生成处理目录和复现实验的说明。",
    )
    add_heading(doc, "6.11 跨数据集综合结果", 2)
    add_body(
        doc,
        "将两个数据集放在一起观察，可以得到比单表排名更稳定的判断。U-KAN 在 BUSI 和 CVC 的 IoU/Dice 均排名第一，说明其优势不是只出现在一种成像模态；no-KAN 在 BUSI 略高于 U-Net、在 CVC 略低于 U-Net，显示 tokenized U 型结构本身的效果受数据特征影响；Attention-U-KAN 在两数据集均未超过 U-KAN，负结果同样具有跨数据集一致性。四模型的相对关系因此形成较完整的证据矩阵。",
    )
    add_body(
        doc,
        "性能提升幅度在两个数据集上不同。BUSI 中 U-KAN 相对 U-Net 的 IoU 增益为 0.0505，相对 no-KAN 为 0.0388；CVC 中对应增益为 0.0070 和 0.0175。前者说明 U-KAN 在弱边界超声上具有更明显综合优势，后者说明在强卷积基线的内镜场景中，KANLinear 仍有贡献，但完整模型相对 U-Net 的边际收益有限。跨数据集报告能够防止只选择最有利数据集夸大创新。",
    )
    add_body(
        doc,
        "Attention-U-KAN 的误差方向也值得综合解读。CVC 中其 Precision 高于 U-KAN，而 Recall 明显降低，表现为保守收缩；BUSI 中 Precision 和 Recall 均略低于 U-KAN，说明注意力不仅没有稳定抑制误检，也损失了部分前景信息。由此推断，四处统一插入同一种注意力并不适配所有尺度，后续改进应优先研究位置和门控信号，而不是继续叠加更多相似模块。",
    )
    add_body(
        doc,
        "若综合精度、速度与模型复杂度，U-Net 是效率基线，no-KAN 是轻参数但不轻计算的结构消融，U-KAN 是精度最优模型，Attention-U-KAN 是未获正向收益的改进尝试。不同模型各自回答不同研究问题，不能把所有表格压缩为单一“冠军模型”。课程论文最终选择 U-KAN 作为主结论，是因为它在两个数据集均取得最高重叠指标，并通过 no-KAN 与第二 seed 获得了更直接的机制证据。",
    )

    add_heading(doc, "7 讨论", 1)
    add_heading(doc, "7.1 U-KAN 的有效性与适用性", 2)
    add_body(
        doc,
        "两个数据集上 U-KAN 均优于 no-KAN，且 BUSI 上的提升更明显。这表明 KANLinear 对高层非线性特征建模具有实际作用，尤其可能有利于噪声强、边界弱和形态不规则的超声场景。但本文结果只支持“在当前固定协议下具有稳定优势”，不能推导为 KAN 在所有分割任务上普遍优于 CNN 或 MLP。",
    )
    add_body(
        doc,
        "BUSI 与 CVC 的差异说明新模块的收益具有任务依赖性。BUSI 图像灰度纹理复杂、边界弱，U-KAN 相对 U-Net 的 Recall 提升明显，可理解为高层可学习边函数帮助模型形成更完整的病灶表示；CVC 图像色彩信息更丰富、分辨率统一，U-Net 已能利用卷积和跳跃连接建立较强基线，U-KAN 的边际提升因而较小。模型创新是否有效，应在具体数据分布和对照强度下判断。",
    )
    add_body(
        doc,
        "U-KAN 相对 no-KAN 在两个数据集和 BUSI 两个 seed 中均保持领先，是本文最直接的算法证据。这个结论比 U-KAN 相对 U-Net 的比较更有针对性，因为前者控制了主体拓扑。与此同时，no-KAN 仍在 BUSI 上超过 U-Net，提示 tokenized 编码、解码路径和通道配置也贡献了性能。完整结论应是“KANLinear 在 U-KAN 拓扑上提供额外收益”，而不是把全部提升归因于单一模块。",
    )
    add_body(
        doc,
        "从部署视角看，U-KAN 更适合作为精度优先的研究模型，而不是未经优化的实时替代方案。其参数量低于 U-Net，却因样条和 token 操作产生更高时延，反映了深度学习系统中参数效率与硬件效率的差异。后续若要提升实用性，需要分析每层耗时、减少 KANLinear 调用次数、降低 token 维度或使用更适合 GPU 的样条实现，而不能只继续压缩参数量。",
    )
    add_heading(doc, "7.2 Attention-U-KAN 未稳定提升的原因", 2)
    add_body(
        doc,
        "注意力模块没有超过原始 U-KAN，可能有四方面原因。第一，模块结构较简单，只在 skip 相加后进行重标定，未显式建模编码器与解码器之间的语义差异；第二，小规模医学数据上额外参数可能增加过拟合风险；第三，连续四处注意力可能过度抑制低响应边界，使 Precision 上升而 Recall 下降；第四，U-KAN 本身已经通过 KANLayer 与 depthwise convolution 进行特征重组，简单注意力与其可能存在功能冗余。因此，“加入注意力”本身不是创新有效性的充分条件。",
    )
    add_body(
        doc,
        "该负结果具有方法论价值。若只展示 U-KAN 和最好基线，论文可以得到更简洁的正向叙事，却无法说明改进尝试经过何种检验。保留 Attention-U-KAN 使研究过程更完整：先根据弱边界问题提出注意力假设，再实现模块并统一训练，最后根据 Precision/Recall 和可视化解释失败。课程论文的创新不仅体现在最终超过基线，也体现在能够提出假设、设计对照并接受不符合预期的结果。",
    )
    add_body(
        doc,
        "当前注意力放在 skip 相加之后，编码和解码特征在进入模块前已直接混合。更有针对性的方案是采用 Attention U-Net 的 attention gate 思路，以解码器语义作为门控信号筛选编码器特征[5]；或者只在高层 skip 使用注意力，保留低层弱边界细节；还可以比较仅通道、仅空间和通道—空间串联三种消融。若开展这些实验，应继续保持参数、训练预算和评估口径一致，避免在失败后只为新模型单独调参。",
    )
    add_heading(doc, "7.3 与官方参考结果的差异", 2)
    add_table(
        doc,
        "表 11 本地复现与 U-KAN 官方 README 参考结果",
        ["项目", "官方 IoU", "官方 Dice/F1", "本文 IoU", "本文 Dice", "说明"],
        [
            ["BUSI U-KAN", "0.6526", "0.7875", "0.6874", "0.8147", "本地单次结果高于官方表中单 run 参考"],
            ["BUSI no-KAN", "0.6349", "0.7707", "0.6486", "0.7869", "KAN 优于 no-KAN 的趋势一致"],
            ["CVC U-KAN", "0.8561", "0.9219", "0.7874", "0.8810", "低于官方参考，协议并不完全相同"],
        ],
        [3.1, 1.7, 2.0, 1.7, 1.7, 5.6],
        "U-KAN 官方 README 与本项目 evaluate.py 结果；不同协议数值不可视为严格横向排名",
        8.8,
    )
    add_body(
        doc,
        "U-KAN 原论文与官方代码仓库提供了公开实验入口[1,8]。官方训练入口默认 400 epoch，并明确提示报告结果与 seed2981、6142、1187 的多次运行有关；本文采用固定 split、100 epoch，并只对 BUSI 的核心 KAN/no-KAN 对照补做第二个 seed。两者在数据处理、训练轮数、随机运行数量和 checkpoint 上均可能不同。因此，本文定位为“协议可控的课程复现与工程诊断”，不宣称完全复刻官方数值。BUSI 达到较好结果证明实现具有有效性；CVC 的差距则通过继续训练实验得到更谨慎解释。",
    )
    add_body(
        doc,
        "算法复现可以分为代码复跑、数值复现和结论复现三个层次。代码复跑要求官方项目在指定环境中成功执行；数值复现要求尽可能匹配论文数据、划分、超参数和随机过程；结论复现则关注主要比较关系是否在合理协议下再次出现。本文重新实现课程工程，没有直接使用官方 checkpoint，训练轮数和部分数据协议也不同，因此不属于严格数值复现；但 U-KAN 相对 no-KAN 的优势方向、KAN 模块的有效性以及注意效率代价等核心判断得到了本地证据支持，属于结论层面的部分复现。",
    )
    add_body(
        doc,
        "BUSI 本地 U-KAN 指标高于官方表中单项参考值，并不意味着本文实现必然优于原论文；CVC 低于官方值也不自动表示实现错误。公开表格可能对应不同运行、不同划分或汇总方式，只有协议完全一致时才能进行严格排名。本文将官方结果单独列出并明确不可直接横向比较，目的在于展示复现差异，而不是借用公开数字为本地模型背书。",
    )
    add_heading(doc, "7.4 实验思考过程与证据链", 2)
    add_body(
        doc,
        "本项目的实验推进不是预先一次性确定全部表格，而是由结果中的疑问推动。第一轮 BUSI 曲线出现 no-KAN loss 偏高、验证指标局部跳升的现象。直觉上这可能像“偶然蒙对”，但直觉本身不是证据。进一步分析发现 loss 与阈值化指标并非同一量，仍无法排除 seed 偶然性，于是设计 seed6142 对照。新结果中绝对指标下降但 U-KAN 仍领先，最终把结论从“某次最优值更高”修正为“不同随机条件下相对方向一致”。",
    )
    add_body(
        doc,
        "第二轮 CVC 曲线中，部分模型最佳点接近训练末期，引出“100 epoch 没有收敛”的猜测。本文没有仅凭图形延长所有实验，也没有直接引用官方更高 IoU 断定训练不足，而是选择主模型 U-KAN 的 best checkpoint 继续训练 50 epoch。续训未超过原始峰值，且末段变化很小，因此否定了最简单的训练不足解释。剩余差异被收敛为数据划分、预处理、评价协议和多 seed 汇总等更合理因素。",
    )
    add_body(
        doc,
        "上述过程体现了从观察、假设、控制变量到结论修正的完整链条。观察负责发现异常，机制分析提出多个可能原因，补充实验只改变一个关键变量，结果再决定保留或否定假设。论文中同时给出原始曲线、诊断流程、补实验表和谨慎结论，使教师能够看到思考过程，而不是只看到最终最优数字。这也是本文区别于简单代码复跑的主要实践价值。",
    )
    add_heading(doc, "7.5 局限与后续改进", 2)
    add_numbered_items(
        doc,
        [
            "数据层面仅使用两个二维公开数据集，且没有进行三 seed 完整均值与方差统计。",
            "训练轮数和算力受课程项目条件限制，未完全复刻官方 400 epoch 协议，也未系统搜索超参数。",
            "当前损失只包含 BCE 与 Dice，尚未加入 Boundary Loss、Tversky/Focal Tversky Loss 或困难样本重加权[16-18]。",
            "Attention-U-KAN 的插入方式较直接，后续可尝试 attention gate、跨层融合或仅在高层 skip 使用注意力。",
            "KAN/tokenized 结构推理开销较大，后续可尝试减少 KAN block、共享样条参数、轻量化通道或算子融合。",
            "可增加 ISIC、Synapse 等数据集，以检验跨模态和多类别分割泛化能力。",
        ],
    )
    add_body(
        doc,
        "除上述技术局限外，本文还存在验证范围限制。BUSI 和 CVC 都是二维二分类数据，不能代表三维 CT/MRI、多器官多类别和跨中心泛化。训练集与验证集来自同一公开数据源，也没有外部测试集，因此结果主要反映同分布性能。若用于真实临床研究，还需进行患者级划分核查、跨设备验证、置信度校准、统计显著性分析和医生参与的误差评估。",
    )
    add_body(
        doc,
        "下一阶段可按优先级推进。首先完成第三随机种子并报告均值±标准差或 bootstrap 置信区间，增强统计可靠性；其次在现有 per-image 与病灶面积分层结果上增加配对显著性检验；再次针对边界错误引入 Boundary Loss 或 Tversky/Focal Tversky Loss[16-18]；随后开展更精细的注意力位置消融；最后再考虑 400 epoch 官方协议和更多数据集。该顺序优先解决证据不足，再扩展模型复杂度，避免在实验基础尚不稳定时堆叠模块。",
    )
    add_heading(doc, "7.6 临床解释、伦理与可靠性边界", 2)
    add_body(
        doc,
        "本文使用公开、去标识化数据开展算法课程实验，不接触患者身份信息，也不将模型输出用于真实诊疗。尽管 U-KAN 在验证集上取得较高 Dice，其预测仍可能在弱边界、小病灶、反光和褶皱场景中失败。医学人工智能系统不能仅凭平均指标进入临床，必须经过外部数据验证、设备与人群偏差评估、医生复核流程和相应伦理审批。",
    )
    add_body(
        doc,
        "分割模型的临床风险具有不对称性。筛查任务通常更关注漏检，Recall 下降可能比少量假阳性更严重；精确测量和手术规划则对边界外扩同样敏感，需要兼顾 Precision 与轮廓距离指标。本文主表没有包含 Hausdorff Distance 和 Average Surface Distance，因此只能评价区域重叠和像素分类，不能完整证明几何边界满足临床要求。后续应根据应用目的补充表面距离与医生评分。",
    )
    add_body(
        doc,
        "可靠部署还需要处理模型置信度和失败检测。当前固定阈值输出确定性 mask，没有估计不确定性；当输入来自不同设备或图像质量明显下降时，模型仍可能给出高置信错误。可通过深度集成、Monte Carlo dropout、测试时增强或校准方法生成不确定性图，并将高风险样本交由人工复核。系统目标应是辅助医生提高一致性，而不是以单一网络替代临床判断。",
    )

    add_heading(doc, "8 结论", 1)
    add_body(
        doc,
        "本文围绕 U-KAN 医学图像分割算法完成了课程级完整复现。项目对 BUSI 与 CVC-ClinicDB 进行二次整理，构建 U-Net、U-KAN(no-KAN)、U-KAN 和 Attention-U-KAN 四类模型，并建立统一训练、全验证集评估、预测保存和图表生成流程。主实验中，U-KAN 在 BUSI 和 CVC 上分别获得 IoU 0.6874/0.7874、Dice 0.8147/0.8810，均为四组模型最优；其相对 no-KAN 的一致提升说明 KANLinear 对高层非线性建模具有实际贡献。",
    )
    add_body(
        doc,
        "Attention-U-KAN 没有稳定超过原始 U-KAN，说明简单注意力并非必然有效。更重要的是，本文没有停留在单次最优指标：针对 BUSI no-KAN loss 与 IoU 跳变的矛盾，补做 seed6142 稳定性实验；针对 CVC best epoch 靠后的现象，从 best checkpoint 继续训练 50 epoch。补充结果表明 KAN 优势不是单次偶然峰值，而 CVC 与官方参考差距也不能仅归因于训练不足。最终，项目形成了从数据处理、模型复现、实验诊断、结果讨论到 Git 版本管理和 Word 论文生成的完整闭环，满足课程对算法原理、模型搭建、实验平台、训练过程、结果分析、来源说明和工程复现的要求。",
    )
    add_body(
        doc,
        "综合研究假设，H1 在两个数据集上得到支持，但 CVC 的提升幅度较小；H2 得到两个数据集和 BUSI 两个 seed 的方向性支持；H3 未得到支持，注意力模型表现出更保守的预测倾向；H4 被继续训练实验否定。由此可见，本研究的主要贡献并非宣称所有新增模块都有效，而是通过受控对照确定 KANLinear 的实际贡献，并用补充实验缩小对异常现象的解释空间。",
    )

    doc.add_page_break()
    add_heading(doc, "9 参考文献", 1)
    references = [
        "[1] LI C, LIU X, LI W, et al. U-KAN makes strong backbone for medical image segmentation and generation[C]//Proceedings of the AAAI Conference on Artificial Intelligence. 2025, 39(5): 4652-4660. DOI:10.1609/aaai.v39i5.32491.",
        "[2] LIU Z, WANG Y, VAIDYA S, et al. KAN: Kolmogorov-Arnold networks[EB/OL]. arXiv:2404.19756, 2024[2026-06-22]. https://arxiv.org/abs/2404.19756.",
        "[3] RONNEBERGER O, FISCHER P, BROX T. U-Net: Convolutional networks for biomedical image segmentation[C]//Medical Image Computing and Computer-Assisted Intervention-MICCAI 2015. Cham: Springer, 2015: 234-241. DOI:10.1007/978-3-319-24574-4_28.",
        "[4] WOO S, PARK J, LEE J Y, et al. CBAM: Convolutional block attention module[C]//Computer Vision-ECCV 2018. Cham: Springer, 2018: 3-19. DOI:10.1007/978-3-030-01234-2_1.",
        "[5] OKTAY O, SCHLEMPER J, LE FOLGOC L, et al. Attention U-Net: Learning where to look for the pancreas[EB/OL]. arXiv:1804.03999, 2018[2026-06-22]. https://arxiv.org/abs/1804.03999.",
        "[6] AL-DHABYANI W, GOMAA M, KHALED H, et al. Dataset of breast ultrasound images[J]. Data in Brief, 2020, 28: 104863. DOI:10.1016/j.dib.2019.104863.",
        "[7] VÁZQUEZ D, BERNAL J, SÁNCHEZ F J, et al. A benchmark for endoluminal scene segmentation of colonoscopy images[J]. Journal of Healthcare Engineering, 2017, 2017: 1-9. DOI:10.1155/2017/4037190.",
        f"[8] CUHK-AIM GROUP. U-KAN official PyTorch implementation[EB/OL]. [2026-06-22]. {GITHUB_URL.replace('Simon-Tisa/AI_CourseWork.git', 'CUHK-AIM-Group/U-KAN')}.",
        "[9] PYTORCH CONTRIBUTORS. PyTorch documentation: Adam, CosineAnnealingLR and BCEWithLogitsLoss[EB/OL]. [2026-06-22]. https://docs.pytorch.org/docs/stable/.",
        "[10] ALBUMENTATIONS TEAM. Albumentations documentation[EB/OL]. [2026-06-22]. https://albumentations.ai/docs/.",
        "[11] WANG H, ZHAO Z, LIU Q, et al. ResU-KAN: A medical image segmentation model integrating residual convolutional attention and atrous spatial pyramid pooling[J]. Applied Intelligence, 2025, 55(7): 568. DOI:10.1007/s10489-025-06467-5.",
        "[12] XU J, GAO H, WANG Z. KC-UNet: Enhancing U-Net with KAN and CBAM for medical image segmentation[J]. IEEE Access, 2025, 13: 153788-153797. DOI:10.1109/ACCESS.2025.3605148.",
        "[13] WU Y, LI T, WANG Z, et al. TransUKAN: Computing-efficient hybrid KAN-Transformer for enhanced medical image segmentation[EB/OL]. arXiv:2409.14676, 2024[2026-06-22]. https://arxiv.org/abs/2409.14676.",
        "[14] SU C, LUO X, LI S, et al. VMKLA-UNet: Vision Mamba with KAN linear attention U-Net[J]. Scientific Reports, 2025, 15(1): 13258. DOI:10.1038/s41598-025-97397-2.",
        "[15] EELBODE T, BERTELS J, BERMAN M, et al. Optimization for medical image segmentation: Theory and practice when evaluating with Dice score or Jaccard index[J]. IEEE Transactions on Medical Imaging, 2020, 39(11): 3679-3690. DOI:10.1109/TMI.2020.3002417.",
        "[16] SALEHI S S M, ERDOGMUS D, GHOLIPOUR A. Tversky loss function for image segmentation using 3D fully convolutional deep networks[C]//Machine Learning in Medical Imaging. Cham: Springer, 2017: 379-387. DOI:10.1007/978-3-319-67389-9_44.",
        "[17] KERVADEC H, BOUCHTIBA J, DESROSIERS C, et al. Boundary loss for highly unbalanced segmentation[C]//Proceedings of the 2nd International Conference on Medical Imaging with Deep Learning. PMLR, 2019, 102: 285-296. https://proceedings.mlr.press/v102/kervadec19a.html.",
        "[18] ABRAHAM N, KHAN N M. A novel focal Tversky loss function with improved Attention U-Net for lesion segmentation[C]//2019 IEEE 16th International Symposium on Biomedical Imaging. 2019: 683-687. DOI:10.1109/ISBI.2019.8759329.",
    ]
    for ref in references:
        add_reference(doc, ref)

    doc.add_page_break()
    add_heading(doc, "附录 A GitHub 源代码链接与工程复现说明", 1)
    add_heading(doc, "A.1 仓库与分支", 2)
    add_body(
        doc,
        f"远程仓库为 {GITHUB_URL}，课程项目位于 ukan-course-paper 目录，开发分支为 course-paper-ukan。项目使用 Git 分阶段记录数据处理、模型实现、CVC 扩展实验、补充诊断、论文正文和最终质量审计。提交论文前应再次执行 git push origin course-paper-ukan，确认远程仓库包含最终 Word、README 和实验结果。",
    )
    add_figure(doc, git_fig, "图 24 本地 Git 分支状态与关键提交记录", "作者根据本地仓库 git status 和 git log 生成", 16.0)
    add_heading(doc, "A.2 README 与复现入口", 2)
    add_body(
        doc,
        "README 提供环境诊断、依赖安装、原始数据目录、BUSI/CVC 数据处理、固定 split、smoke test、八组主实验训练、统一评估、曲线绘制、预测可视化、结果汇总和论文生成命令。run_python.ps1 优先调用 C:\\ProgramData\\Anaconda\\envs\\torch\\python.exe，以减少系统 Python 与训练环境混用造成的依赖问题。",
    )
    add_heading(doc, "A.3 项目结构", 2)
    structure = (
        "ukan-course-paper/\n"
        "├── configs/        实验 YAML 配置\n"
        "├── data/           raw、processed 与 splits\n"
        "├── scripts/        数据准备、训练、评估、绘图和论文生成\n"
        "├── src/            模型、数据集、损失、指标和工具函数\n"
        "├── tests/          模型、指标和数据处理测试\n"
        "├── experiments/    日志、checkpoint、metrics、预测和实验图\n"
        "└── paper/          正文、Word、表格、图片和质量验收材料"
    )
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(structure)
    set_run_font(r, 10, east_asia="等线", ascii_font="Consolas")

    add_heading(doc, "附录 B 公开数据集二次整理说明", 1)
    add_body(
        doc,
        "本项目没有自行采集或标注原始临床数据，因此不将 BUSI/CVC 宣称为原创数据集。课程加分点来自对公开数据的二次整理质量：建立统一 raw/processed 目录；处理 BUSI 多 mask；统一二值化与文件命名；生成固定 split；统计全部 mask 前景比例；生成样本图和数据报告；保证四组模型共享同一划分。所有处理均由脚本实现，能够从原始公开数据重新构建实验目录。",
    )

    add_heading(doc, "附录 C 论文格式与图表来源说明", 1)
    add_body(
        doc,
        "论文采用 A4 纸，页边距为左 3 cm、右 2 cm、上 2.5 cm、下 2.5 cm；正文使用小四号宋体和 1.5 倍行距，章节标题采用宋体加粗并使用 Word Heading 样式。正文页码从第一页开始，以阿拉伯数字置于页脚右侧；封面和最后的成绩评定页不编页码。表题位于表格上方，图题位于图片下方，表格下方注明资料来源。公式置于无边框表格中并按章节编号。数据集统计、训练曲线、预测对比、失败分析和补充实验图均由 MATLAB 直接读取项目数据生成；经典结构图从本地原论文 PDF 提取并标注 Figure 与参考文献编号；本文创新结构保留作者自绘图。",
    )

    add_heading(doc, "附录 D 课程要求与加分项落实情况", 1)
    add_table(
        doc,
        "表 12 课程要求与项目落实情况",
        ["课程要求/加分项", "本文对应内容", "所在位置", "状态"],
        [
            ["算法原理与模型搭建", "U-Net、KANLinear、U-KAN、no-KAN、Attention-U-KAN", "第 4 章", "完成"],
            ["实验平台与训练过程", "环境、参数、增强、loss、checkpoint 与曲线", "第 5、6 章", "完成"],
            ["定量与定性评估", "五项指标、效率、预测图和错误案例", "第 6 章", "完成"],
            ["异常诊断与讨论", "seed 稳定性、继续训练、官方差异和局限", "第 6、7 章", "完成"],
            ["课程论文来源说明", "论文、开源代码、数据集和 LLM 使用说明", "第 1 章", "完成"],
            ["每图来源标注", "作者自绘、原论文图、MATLAB 生成和真实运行截图", "全部图题", "完成"],
            ["代码运行截图", "真实训练后段、checkpoint 保存与统一评估输出", "图 23、第 6.10 节", "完成"],
            ["参考文献与正文引用", "18 条文献真实性核验、格式统一、正文引用闭环", "第 9 章及相关正文", "完成"],
            ["GitHub 与 README", "仓库、分支、运行指南和工程结构", "附录 A", "本地完成，提交前确认 push"],
            ["公开数据集整理", "多 mask 合并、二值化、固定 split 和统计", "第 5 章、附录 B", "完成"],
            ["论文排版", "小四、1.5 倍行距、标题/图表/公式/参考文献统一", "全文、附录 C", "完成"],
            ["独立思考与额外实践", "曲线疑问、补实验验证和负结果分析", "第 6、7 章", "完成"],
        ],
        [4.0, 6.7, 3.1, 2.4],
        "作者依据《人工智能》课程论文要求与项目最终材料逐项核对",
        8.7,
    )

    add_evaluation_page(doc)

    return doc


def main() -> int:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    doc = build_document()
    doc.save(TARGET)
    print(f"wrote={TARGET}")
    print(f"backup={BACKUP}")
    print(f"figures={FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
