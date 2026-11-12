#!/usr/bin/env python3
"""Read-only comparison of PDF exports and PPTX slide text.

Slides with diagrams, charts and screenshots need independent visual review.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from xml.etree import ElementTree

try:
    from scripts.audit_content_overlap import Extracted, extract, sha, tokens, validate_output_dir
    from scripts.audit_material_variants import inventory
    from scripts.audit_xr_pairs import compare_records
except ModuleNotFoundError:
    from audit_content_overlap import Extracted, extract, sha, tokens, validate_output_dir
    from audit_material_variants import inventory
    from audit_xr_pairs import compare_records

SLIDE = re.compile(r"ppt/slides/slide([1-9][0-9]*)\.xml$")
TAG = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"
MAX_BYTES = 25 * 1024 * 1024
MAX_CHARS = 700_000
MAX_SLIDES = 300


def extract_pptx(path: Path, root: Path) -> Extracted:
    name = path.relative_to(root).as_posix()
    digest = sha(path)
    if path.is_symlink() or path.stat().st_size > MAX_BYTES:
        return Extracted(name, digest, "EXTRACTION_INCOMPLETE", [], [], "LIMIT_BYTES_OR_SYMLINK")
    try:
        with ZipFile(path) as archive:
            slide_files = []
            for item in archive.infolist():
                match = SLIDE.fullmatch(item.filename)
                if match:
                    slide_files.append((int(match.group(1)), item))
            slide_files.sort(key=lambda row: row[0])
            segments = []
            count = 0
            warning = "LIMIT_SLIDES" if len(slide_files) > MAX_SLIDES else ""
            for number, entry in slide_files[:MAX_SLIDES]:
                if entry.file_size > 4 * 1024 * 1024 or (entry.file_size > 1_000_000 and
                    entry.file_size > 200 * max(entry.compress_size, 1)):
                    return Extracted(name, digest, "EXTRACTION_INCOMPLETE", [], [], "UNSAFE_SLIDE_XML")
                root_xml = ElementTree.fromstring(archive.read(entry))
                content = " ".join((node.text or "") for node in root_xml.iter(TAG)).strip()
                if content:
                    remaining = MAX_CHARS - count
                    segments.append({"location": f"slajd {number}", "text": content[:remaining]})
                    count += min(len(content), remaining)
                if count >= MAX_CHARS:
                    warning = "LIMIT_CHARS"
                    break
        words = tokens(" ".join(item["text"] for item in segments))
        return Extracted(name, digest, "EXTRACTION_INCOMPLETE" if warning or not words else "EXTRACTED",
                         segments, words, warning or ("NO_TEXT" if not words else ""))
    except (OSError, BadZipFile, KeyError, ValueError, ElementTree.ParseError, RuntimeError) as exc:
        return Extracted(name, digest, "EXTRACTION_INCOMPLETE", [], [],
                         f"{type(exc).__name__}: {str(exc)[:80]}")


def compare(root: Path) -> dict:
    pairs = []
    variants = inventory(root)["format_variants"]
    for row in variants:
        if row["family"] != "pdf_pptx":
            continue
        names = row["files"]
        pdf = next((root / f for f in names if f.lower().endswith(".pdf")), None)
        pptx = next((root / f for f in names if f.lower().endswith(".pptx")), None)
        if pdf is None or pptx is None or not pdf.is_file() or not pptx.is_file():
            pairs.append({"files":names, "classification":"MISSING_INPUT", "decision":"REVIEW_REQUIRED"})
            continue
        a = extract(pdf, root)
        b = extract_pptx(pptx, root)
        result = compare_records(a, b)
        result["classification"] = ("EXTRACTION_INCOMPLETE"
                                    if a.status != "EXTRACTED" or b.status != "EXTRACTED"
                                    else "FORMAT_TEXT_MISMATCH_CANDIDATE"
                                    if (result["coverage_shorter_5gram"] or 0) < .25
                                    else "FORMAT_TEXT_SIMILAR_CANDIDATE"
                                    if (result["coverage_shorter_5gram"] or 0) >= .75
                                    else "FORMAT_DIFFERENCE_REVIEW")
        result["files"] = names
        result["decision"] = "REVIEW_REQUIRED"
        # A slide extraction may miss embedded videos, notes, equations, images,
        # charts and text in grouped shapes, so always require visual inspection.
        pairs.append(result)
    return {"schema_version":"1.0.0", "pairs":pairs,
            "limitations":["PPTX slides are not rendered; images/charts/equations omitted.",
                           "Matching only compares extracted visible slide text to PDF text.",
                           "No automatic duplicate or archiving decisions."]}


def markdown(data: dict) -> str:
    lines = ["# PDF–PPTX slide-text audit", "",
             "| Pair | Words (PDF/PPTX) | 5-gram coverage | Classification |",
             "| --- | ---: | ---: | --- |"]
    for row in data["pairs"]:
        names = row["files"]
        coverage = row.get("coverage_shorter_5gram")
        measure = f"{coverage:.1%}" if coverage is not None else "n/a"
        wordcount = f"{row.get('a_word_count', 0)}/{row.get('b_word_count', 0)}"
        lines.append(f"| {Path(names[0]).name} / {Path(names[1]).name} | {wordcount} | {measure} | {row['classification']} |")
    lines.extend(["", "All comparisons are unverified; visual QA required.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("files"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root, destination = args.root.resolve(), args.output_dir.resolve()
    validate_output_dir(root.parent, destination)
    data = compare(root)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "slides_comparison.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "slides_comparison.md").write_text(markdown(data), encoding="utf-8")
    print(markdown(data))


if __name__ == "__main__":
    main()
