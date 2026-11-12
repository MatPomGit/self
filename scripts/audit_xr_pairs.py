#!/usr/bin/env python3
"""Read-only page-level lexical comparison of paired XR teaching materials.

This reports evidence, not whether exercises are pedagogically interchangeable.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.audit_content_overlap import (
        Extracted, common_witness, extract, grams, tokens,
        validate_output_dir, revision,
    )
except ModuleNotFoundError:
    from audit_content_overlap import (
        Extracted, common_witness, extract, grams, tokens,
        validate_output_dir, revision,
    )

ROOT_DIR = "wirtualna-i-rozszerzona-rzeczywistosc"


def compare_records(a: Extracted, b: Extracted) -> dict:
    ag, bg = grams(a.words), grams(b.words)
    shared = ag & bg
    union = ag | bg
    shorter = min(len(ag), len(bg))
    overlap = len(shared) / shorter if shorter else None
    # Separate directional coverage helps identify an abridged or extended release.
    a_coverage = len(shared) / len(ag) if ag else None
    b_coverage = len(shared) / len(bg) if bg else None
    page_matches = []
    if a.status == "EXTRACTED" and b.status == "EXTRACTED":
        for i, ap in enumerate(a.segments):
            aw = grams(tokens(ap["text"]))
            candidates = []
            for j, bp in enumerate(b.segments):
                bw = grams(tokens(bp["text"]))
                smaller = min(len(aw), len(bw))
                score = len(aw & bw) / smaller if smaller else 0.0
                if score >= 0.15:
                    candidates.append({
                        "b_page": j + 1,
                        "b_location": bp["location"],
                        "coverage_shorter_5gram": round(score, 4),
                    })
            if candidates:
                page_matches.append({
                    "a_page": i + 1,
                    "a_location": ap["location"],
                    "matches": sorted(
                        candidates, key=lambda x: -x["coverage_shorter_5gram"]
                    )[:3],
                })
    return {
        "a_path": a.path, "b_path": b.path,
        "a_sha256": a.source_hash, "b_sha256": b.source_hash,
        "a_status": a.status, "b_status": b.status,
        "a_warning": a.warning, "b_warning": b.warning,
        "a_word_count": len(a.words), "b_word_count": len(b.words),
        "a_pages_extracted": len(a.segments), "b_pages_extracted": len(b.segments),
        "coverage_shorter_5gram": round(overlap, 4) if overlap is not None else None,
        "coverage_a_5gram": round(a_coverage, 4) if a_coverage is not None else None,
        "coverage_b_5gram": round(b_coverage, 4) if b_coverage is not None else None,
        "jaccard_5gram": round(len(shared) / len(union), 4) if union else None,
        "matched_pages": page_matches,
        "shared_excerpts": common_witness(a, b) if shared else [],
        "classification": (
            "EXTRACTION_INCOMPLETE" if a.status != "EXTRACTED" or b.status != "EXTRACTED"
            else "TEXT_OVERLAP_CANDIDATE" if overlap is not None and overlap >= 0.23
            else "LOW_LEXICAL_OVERLAP"
        ),
        "decision": "REVIEW_REQUIRED",
    }


def audit(root: Path) -> dict:
    pairs = []
    for n in range(1, 8):
        base = root / ROOT_DIR
        first = base / f"wirr_lab_{n:02d}.pdf"
        second = base / f"Lab_{n}_XR.pdf"
        if (not first.is_file() or not second.is_file()
                or first.is_symlink() or second.is_symlink()):
            pairs.append({"lab": n, "classification": "MISSING_INPUT",
                          "decision": "REVIEW_REQUIRED",
                          "files": [str(first.relative_to(root)), str(second.relative_to(root))]})
            continue
        result = compare_records(extract(first, root), extract(second, root))
        result["lab"] = n
        pairs.append(result)
    return {"schema_version": "1.0.0", "source_revision": revision(root.parent),
            "scope": ROOT_DIR, "pairs": pairs,
            "limitations": [
                "Lexical matching is not semantic equivalence.",
                "Shared boilerplate or citations can inflate similarity.",
                "Text extraction does not inspect diagrams, figures or task screenshots.",
                "No input files are modified; no merge/supersede decision is automated.",
            ]}


def markdown(result: dict) -> str:
    lines = ["# XR laboratory pair comparison", "",
             f"Revision: `{result['source_revision']}`", "",
             "| Lab | Classification | A/B words | Shorter 5-gram coverage | Review |",
             "| --- | --- | ---: | ---: | --- |"]
    for item in result["pairs"]:
        words = (f"{item['a_word_count']}/{item['b_word_count']}"
                 if "a_word_count" in item else "–")
        coverage = item.get("coverage_shorter_5gram")
        value = f"{coverage:.1%}" if coverage is not None else "n/a"
        lines.append(f"| {item['lab']:02d} | {item['classification']} | "
                     f"{words} | {value} | REVIEW_REQUIRED |")
    lines.extend(["", "All candidates require comparison of educational objectives,",
                  "unique assignments, evaluation criteria, tables, and figures.",
                  "No recommendation to archive a file follows solely from these scores.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("files"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output_dir.resolve()
    if not root.is_dir():
        parser.error(f"Missing root: {root}")
    validate_output_dir(root.parent, out)
    report = audit(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "xr_pairs.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "xr_pairs.md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
