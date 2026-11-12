#!/usr/bin/env python3
"""Extract and compare four candidate reports; never alter report sources.

The output is an evidence bundle for editorial review, not a consolidation.
All inputs are explicit allowlisted public report paths.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.audit_content_overlap import (
        Extracted, extract, grams, revision, sha, tokens, validate_output_dir,
    )
except ModuleNotFoundError:
    from audit_content_overlap import (
        Extracted, extract, grams, revision, sha, tokens, validate_output_dir,
    )

INPUTS = {
    "isaac_architecture": "files/inne/analizy/isaac_sim.docx",
    "isaac_glossary": "files/inne/analizy/isaac_sim_pojecia.pdf",
    "ndd_review": "files/inne/analizy/tele_ndd.docx",
    "ndd_telehealth": "files/inne/analizy/teled_ndd.docx",
}
CANONICAL = "docs/consolidated/isaac_lab.md"


def coverage(a: list[str], b: list[str]) -> dict:
    ag, bg = grams(a), grams(b)
    common = ag & bg
    denom = min(len(ag), len(bg))
    return {
        "shared_5grams": len(common),
        "coverage_shorter_5gram": round(len(common) / denom, 4) if denom else None,
        "coverage_a_5gram": round(len(common) / len(ag), 4) if ag else None,
        "coverage_b_5gram": round(len(common) / len(bg), 4) if bg else None,
    }


def paragraph_review(source: Extracted, reference: Extracted, limit: int = 40) -> list[dict]:
    """Prioritize passages with little exact lexical reuse; no semantic claim."""
    reference_grams = grams(reference.words)
    rows = []
    for p in source.segments:
        words = tokens(p["text"])
        if len(words) < 14:
            continue
        part_grams = grams(words)
        score = len(part_grams & reference_grams) / len(part_grams) if part_grams else None
        rows.append({
            "location": p["location"],
            "word_count": len(words),
            "coverage_in_reference": round(score, 4) if score is not None else None,
            "text": p["text"][:3000],
        })
    # Keep source order for editorial traceability, but cap the review summary.
    return sorted(rows, key=lambda x: (
        x["coverage_in_reference"] is None,
        x["coverage_in_reference"] or 0, -x["word_count"],
        x["location"],
    ))[:limit]


def extract_allowlisted(root: Path, relative: str) -> Extracted:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing or symlinked allowlisted input: {relative}")
    record = extract(path, root)
    if record.status != "EXTRACTED":
        raise ValueError(f"Incomplete extraction of {relative}: {record.warning}")
    return record


def analyze(root: Path) -> dict:
    source_records = {key: extract_allowlisted(root, path)
                      for key, path in INPUTS.items()}
    canonical_path = root / CANONICAL
    if not canonical_path.is_file() or canonical_path.is_symlink():
        raise ValueError(f"Missing canonical document: {CANONICAL}")
    canonical_text = canonical_path.read_text(encoding="utf-8")
    canonical = Extracted(CANONICAL, sha(canonical_path), "EXTRACTED",
                          [{"location": "full source", "text": canonical_text}],
                          tokens(canonical_text))
    all_records = dict(source_records, isaac_canonical=canonical)
    pairs = {}
    for key_a, key_b in [
        ("isaac_architecture", "isaac_canonical"),
        ("isaac_glossary", "isaac_canonical"),
        ("isaac_architecture", "isaac_glossary"),
        ("ndd_review", "ndd_telehealth"),
    ]:
        a, b = all_records[key_a], all_records[key_b]
        pairs[key_a + "__" + key_b] = {
            "a": key_a, "b": key_b,
            "a_sha256": a.source_hash,
            "b_sha256": b.source_hash,
            **coverage(a.words, b.words),
            "decision": "REVIEW_REQUIRED",
            "passages_to_review": paragraph_review(a, b),
        }
    return {
        "schema_version": "1.0.0",
        "revision": revision(root),
        "sources": {
            key: {
                "path": item.path, "sha256": item.source_hash,
                "word_count": len(item.words), "segments": item.segments,
                "status": item.status,
            } for key, item in all_records.items()
        },
        "pairs": pairs,
        "limitations": [
            "Lexical overlap is not semantic equivalence.",
            "PDF figures and DOCX figures/tables require visual review.",
            "Passages with zero lexical overlap may still paraphrase the reference.",
            "No source replacement or automatic archiving is authorized.",
        ],
    }


def summary(report: dict) -> str:
    lines = [
        "# Editorial evidence: Isaac Sim and ADHD/ASD", "",
        f"Source revision: \`{report['revision']}\`", "",
        "| Comparison | Words A/B | 5-gram shorter coverage | Review |",
        "| --- | ---: | ---: | --- |",
    ]
    for key, item in report["pairs"].items():
        a, b = report["sources"][item["a"]], report["sources"][item["b"]]
        score = item["coverage_shorter_5gram"]
        display = f"{score:.1%}" if score is not None else "n/a"
        lines.append(f"| {key} | {a['word_count']}/{b['word_count']} | {display} | REVIEW_REQUIRED |")
    lines.extend(["", "## Source hashes and segment counts"])
    for key, item in report["sources"].items():
        lines.append(f"- {key}: \`{item['path']}\`; SHA-256 \`{item['sha256']}\`; "
                     f"{item['word_count']} words, {len(item['segments'])} segments")
    lines.extend(["", "### Interpretation",
                  "The passages requiring review are in evidence.json. Validate each "
                  "claim, table and citation before authoring a combined report. "
                  "No files were modified.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root, destination = args.root.resolve(), args.output_dir.resolve()
    validate_output_dir(root, destination)
    report = analyze(root)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "evidence.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "summary.md").write_text(summary(report), encoding="utf-8")
    print(summary(report))


if __name__ == "__main__":
    main()
