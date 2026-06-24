from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document


def expand_group(group: str) -> set[int]:
    numbers: set[int] = set()
    for part in re.split(r"[,，]", group):
        part = part.strip()
        match = re.fullmatch(r"(\d+)\s*[-–—]\s*(\d+)", part)
        if match:
            start, end = map(int, match.groups())
            numbers.update(range(start, end + 1))
        elif part.isdigit():
            numbers.add(int(part))
    return numbers


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit numbered citations in the paper.")
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()

    document = Document(args.docx.resolve())
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    reference_heading = next(
        index for index, text in enumerate(paragraphs) if text.endswith("参考文献")
    )
    body = "\n".join(paragraphs[:reference_heading])
    reference_lines = paragraphs[reference_heading + 1 :]

    listed: set[int] = set()
    for line in reference_lines:
        match = re.match(r"^\[(\d+)\]", line)
        if match:
            listed.add(int(match.group(1)))

    cited: set[int] = set()
    for group in re.findall(r"\[([0-9,\-–—，\s]+)\]", body):
        expanded = expand_group(group)
        if expanded and expanded.issubset(listed):
            cited.update(expanded)

    print(f"cited={sorted(cited)}")
    print(f"listed={sorted(listed)}")
    print(f"uncited_references={sorted(listed - cited)}")
    print(f"missing_references={sorted(cited - listed)}")
    print(f"reference_sequence_ok={sorted(listed) == list(range(1, len(listed) + 1))}")

    assert listed
    assert not listed - cited
    assert not cited - listed
    assert sorted(listed) == list(range(1, len(listed) + 1))


if __name__ == "__main__":
    main()
