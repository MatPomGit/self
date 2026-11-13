#!/usr/bin/env python3
"""Summarize editorial review priorities from read-only material audits."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REPORTS = {
    "docx": "format-comparison/format_comparison.json",
    "slides": "slide-comparison/slides_comparison.json",
    "tex": "tex-comparison/tex_comparison.json",
}

def weak_slides(row, threshold=.60):
    out = []
    for page in row.get("matched_pages", []):
        number = page.get("a_page")
        aligned = [m for m in page.get("matches", []) if m.get("b_page") == number]
        if not aligned:
            continue
        best = max(aligned, key=lambda m: m.get("coverage_shorter_5gram", 0))
        if best.get("coverage_shorter_5gram", 0) < threshold:
            out.append({"pdf_page": number, "pptx_slide": number,
                        "coverage": best["coverage_shorter_5gram"]})
    return sorted(out, key=lambda r: r["coverage"])[:7]

def summarize(reports):
    tasks = []
    for kind, report in reports.items():
        for row in report["pairs"]:
            files = row.get("files", [])
            if len(files) != 2 or not all(isinstance(s, str) for s in files):
                continue
            coverage = row.get("coverage_shorter_5gram")
            status = row.get("status", row.get("classification", "UNKNOWN"))
            if kind == "docx":
                if status == "TEXT_VARIANTS_SIMILAR":
                    continue
                priority = "P1" if status in {"FORMAT_MISMATCH_CANDIDATE", "EXTRACTION_INCOMPLETE"} else "P2"
            elif kind == "slides":
                coverage_pdf = row.get("coverage_a_5gram")
                if status == "FORMAT_TEXT_SIMILAR_CANDIDATE" and coverage_pdf is not None and coverage_pdf >= .75:
                    continue
                priority = "P1" if status in {"EXTRACTION_INCOMPLETE", "FORMAT_TEXT_MISMATCH_CANDIDATE"} else "P2"
            else:
                priority = "P1" if status == "EXTRACTION_INCOMPLETE" or (
                    isinstance(coverage, (int, float)) and coverage < .5) else "P2"
            item = {"kind": kind, "priority": priority, "files": files,
                    "status": status, "coverage_shorter_5gram": coverage,
                    "decision": "REVIEW_REQUIRED",
                    "a_sha256": row.get("a_sha256"), "b_sha256": row.get("b_sha256"),
                    "a_words": row.get("a_words", row.get("a_word_count")),
                    "b_words": row.get("b_words", row.get("b_word_count"))}
            if kind == "slides":
                item.update({"pdf_pages": row.get("a_pages_extracted"),
                             "pptx_slides": row.get("b_pages_extracted"),
                             "coverage_pdf": row.get("coverage_a_5gram"),
                             "coverage_pptx": row.get("coverage_b_5gram"),
                             "weak_aligned_pages": weak_slides(row)})
            tasks.append(item)
    tasks.sort(key=lambda row: (row["priority"], row["kind"],
                  row["coverage_shorter_5gram"] is None,
                  row["coverage_shorter_5gram"] or 0, row["files"][0]))
    return {"schema_version": "1.0.0",
            "counts": {kind: len(v["pairs"]) for kind, v in reports.items()},
            "review_tasks": tasks, "decision": "NO_AUTOMATIC_ARCHIVING"}

def markdown(result):
    lines = ["# Material variant editorial review", "",
             "**No automatic deletion, merging or archiving.**", "",
             "| Priority | Files | 5-gram coverage | Status | Weak PDF pages |",
             "| --- | --- | ---: | --- | --- |"]
    for r in result["review_tasks"]:
        names = " / ".join(Path(p).name.replace("|", "") for p in r["files"])
        val = r["coverage_shorter_5gram"]
        cov = f"{val:.1%}" if isinstance(val, (int, float)) else "n/a"
        weak = ", ".join(str(p["pdf_page"]) for p in r.get("weak_aligned_pages", [])) or "–"
        lines.append(f"| {r['priority']} | {names} | {cov} | {r['status']} | {weak} |")
    lines.extend(["", f"Review tasks: **{len(result['review_tasks'])}**.",
                  "All decisions remain REVIEW_REQUIRED."])
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    output = args.output_dir.resolve()
    if any(output == repo / folder or (repo / folder) in output.parents
           for folder in ("files", "docs", "_site")):
        parser.error("Cannot store audit reports inside public directories")
    reports = {}
    for kind, name in REPORTS.items():
        path = args.reports_root / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 10_000_000:
            parser.error(f"Missing or oversized report: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("pairs"), list):
            parser.error(f"Invalid input schema: {path}")
        reports[kind] = data
    result = summarize(reports)
    output.mkdir(parents=True, exist_ok=True)
    (output / "triage.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "triage.md").write_text(markdown(result), encoding="utf-8")
    print(markdown(result))

if __name__ == "__main__":
    main()
