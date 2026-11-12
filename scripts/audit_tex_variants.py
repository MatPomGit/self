#!/usr/bin/env python3
"""Read-only PDF/LaTeX content comparison, not a build or scientific QA."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from scripts.audit_content_overlap import Extracted, extract, sha, tokens, validate_output_dir
    from scripts.audit_material_variants import inventory
    from scripts.audit_xr_pairs import compare_records
except ModuleNotFoundError:
    from audit_content_overlap import Extracted, extract, sha, tokens, validate_output_dir
    from audit_material_variants import inventory
    from audit_xr_pairs import compare_records

MAX_BYTES = 2 * 1024 * 1024
MAX_CHARS = 700_000
HEADINGS = re.compile(r"\\(?:part|chapter|section|subsection|subsubsection|paragraph)\*?\{([^{}]*)\}")
COMMENTS = re.compile(r"(?<!\\)%[^\n]*")
PREAMBLE = re.compile(r"\\begin\{document\}")


def latex_segments(path: Path, root: Path) -> Extracted:
    relative = path.relative_to(root).as_posix()
    digest = sha(path)
    if path.is_symlink() or path.stat().st_size > MAX_BYTES:
        return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", [], [], "LIMIT_BYTES_OR_SYMLINK")
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", [], [], type(exc).__name__)
    if len(source) > MAX_CHARS:
        return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", [], [], "LIMIT_CHARS")
    match = PREAMBLE.search(source)
    if match is None:
        return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", [], [], "NO_DOCUMENT_BODY")
    source = source[match.end():].split(r"\end{document}", 1)[0]
    source = COMMENTS.sub("", source)
    # This is intentionally a conservative lexical approximation, not a LaTeX
    # interpreter. Nested macros and math are retained as approximate words.
    source = re.sub(r"\\(?:input|include|includegraphics|bibliography)\s*(?:\[[^\]]*\])?\s*\{[^}]*\}", " ", source)
    source = re.sub(r"\\(?:begin|end)\{[^}]+\}", "\n", source)
    source = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", " ", source)
    source = re.sub(r"\\[^a-zA-Z\s]", " ", source)
    source = source.replace("{", " ").replace("}", " ")
    source = source.replace("&", " ").replace("$", " ")
    source = re.sub(r"\s+", " ", source).strip()
    # The extraction is lossy; mark complex sources as requiring review.
    words = tokens(source)
    if not words:
        return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", [], [], "NO_TEXT")
    return Extracted(relative, digest, "EXTRACTED", [{"location":"document body", "text":source}], words,
                     "LATEX_APPROXIMATION_REVIEW_REQUIRED")


def compare(root: Path) -> dict:
    pairs = []
    for item in inventory(root)["format_variants"]:
        if item["family"] != "pdf_tex":
            continue
        names = item["files"]
        pdf = next((root / n for n in names if n.lower().endswith(".pdf")), None)
        tex = next((root / n for n in names if n.lower().endswith(".tex")), None)
        if pdf is None or tex is None or not pdf.is_file() or not tex.is_file() or pdf.is_symlink() or tex.is_symlink():
            pairs.append({"files":names, "classification":"MISSING_INPUT", "decision":"REVIEW_REQUIRED"})
            continue
        a, b = extract(pdf, root), latex_segments(tex, root)
        result = compare_records(a, b)
        result["files"] = names
        if a.status != "EXTRACTED" or b.status != "EXTRACTED":
            result["classification"] = "EXTRACTION_INCOMPLETE"
        elif (result["coverage_shorter_5gram"] or 0) < .25:
            result["classification"] = "LOW_LEXICAL_OVERLAP"
        elif result["coverage_shorter_5gram"] >= .75:
            result["classification"] = "HIGH_LEXICAL_OVERLAP"
        else:
            result["classification"] = "REVIEW_DIFFERENCES"
        result["decision"] = "REVIEW_REQUIRED"
        pairs.append(result)
    return {"schema_version":"1.0.0", "pairs":pairs,
            "limitations":["LaTeX macro removal is approximate and not a compilation.",
                           "Included files, diagrams, mathematics and tables require independent review.",
                           "No automatic archive, deletion or supersession."]}


def markdown(report: dict) -> str:
    lines = ["# PDF–TEX text comparison", "",
             "| Pair | Words (PDF / TEX) | 5-gram overlap | Status |",
             "| --- | ---: | ---: | --- |"]
    for item in report["pairs"]:
        label = " / ".join(Path(p).name for p in item["files"])
        value = item.get("coverage_shorter_5gram")
        coverage = "n/a" if value is None else f"{value:.1%}"
        lines.append(f"| {label} | {item.get('a_word_count', 0)} / {item.get('b_word_count', 0)} | {coverage} | {item['classification']} |")
    lines.extend(["", "Requires visual inspection of PDF rendering and separate verification of exercises.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("files"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output_dir.resolve()
    if not root.is_dir():
        parser.error("Missing input root")
    validate_output_dir(root.parent, output)
    report = compare(root)
    output.mkdir(parents=True, exist_ok=True)
    (output / "tex_comparison.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (output / "tex_comparison.md").write_text(markdown(report),encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
