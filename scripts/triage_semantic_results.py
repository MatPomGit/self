#!/usr/bin/env python3
"""Classify *retrieval evidence*, not scientific equivalence, for self#138.

Separate broad content reuse, local repeated assertions, shared references,
shared metadata and weak single-window topical matches. Every output is
UNVERIFIED, and no MERGE/SUPERSEDE recommendation is made.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

try:
    from .audit_content_overlap import validate_output_dir
except ImportError:
    from audit_content_overlap import validate_output_dir


DOI = re.compile(r"(?:doi\s*:?\s*|https?://doi\.org/)?10\.\d{4,9}/[^\s,;]+", re.I)
KEYWORDS = re.compile(r"^\s*(?:słowa\s+kluczowe|keywords?|key\s+words)\s*:",re.I)
REF_TITLE = re.compile(r"^\s*(?:bibliografia|references|piśmiennictwo|literatura\s+cytowana)\b",re.I)
REF_MARKERS = re.compile(r"\[\d{1,3}\]|\bet\s+al\.\s*\(?20\d\d\)?",re.I)
NUMBERED = re.compile(r"(?:[<>≥≤]\s*\d+(?:[,.]\d+)?)|"
                      r"\b\d+(?:[,.]\d+)?\s*(?:%|ms|s|Hz|/min)\b",re.I)


def is_reference(text: str) -> bool:
    """Conservative bibliographic heuristic for quoted passage evidence."""
    normalized = " ".join(text.split())
    doi_count = len(DOI.findall(normalized))
    markers = len(REF_MARKERS.findall(normalized))
    if REF_TITLE.match(normalized):
        return True
    if doi_count >= 1 and ("doi" in normalized.lower() or markers >= 1):
        return True
    return markers >= 3 and re.search(r"\b(?:20[01]\d|19\d\d)\b",normalized) is not None


def classify(pair: dict) -> dict:
    a = float(pair["matched_fraction_a"])
    b = float(pair["matched_fraction_b"])
    cosine = float(pair["max_cosine"])
    evidence = pair.get("evidence", [])
    reference = 0
    keywords = 0
    content = 0
    numeric = []
    for e in evidence:
        lhs, rhs = e["a_excerpt"], e["b_excerpt"]
        if is_reference(lhs) and is_reference(rhs):
            reference += 1
        elif KEYWORDS.match(lhs) and KEYWORDS.match(rhs):
            keywords += 1
        else:
            content += 1
            if NUMBERED.search(lhs) and NUMBERED.search(rhs):
                numeric.append({
                    "a_locator": e["a_locator"],
                    "b_locator": e["b_locator"],
                    "status": "NUMERIC_CLAIM_REVIEW_REQUIRED"
                })
    if reference and not content and not keywords:
        category = "SHARED_BIBLIOGRAPHY_CANDIDATE"
    elif keywords and not content and not reference:
        category = "SHARED_KEYWORDS_CANDIDATE"
    elif min(a,b) >= .35 and content >= 2:
        category = "BROAD_CONTENT_REUSE_CANDIDATE"
    elif content >= 1 and min(a,b) >= .08:
        category = "LOCAL_CONTENT_OVERLAP_CANDIDATE"
    else:
        category = "TOPIC_SIMILARITY_LOW_COVERAGE"
    harmonic = 2*a*b/(a+b) if a+b else 0.0
    ranking_tier = {
        "BROAD_CONTENT_REUSE_CANDIDATE":0,
        "LOCAL_CONTENT_OVERLAP_CANDIDATE":1,
        "TOPIC_SIMILARITY_LOW_COVERAGE":2,
        "SHARED_BIBLIOGRAPHY_CANDIDATE":3,
        "SHARED_KEYWORDS_CANDIDATE":4
    }[category]
    return {
        **pair,
        "triage_class": category,
        "ranking_tier": ranking_tier,
        "harmonic_coverage": round(harmonic,4),
        "ranking_score": round(cosine*harmonic,5),
        "evidence_composition": {
            "content_examples":content,
            "shared_references":reference,
            "shared_keywords":keywords
        },
        "numeric_claims_to_verify":numeric,
        "verified":False
    }


def summarize(report: dict) -> dict:
    if report.get("schema_version") != "0.1.0":
        raise ValueError("Unsupported semantic report schema")
    if report.get("verified") is not False:
        raise ValueError("Expected explicitly unverified input")
    ranked = [classify(p) for p in report["pairs"]]
    ranked.sort(key=lambda p: (p["ranking_tier"], -p["ranking_score"],
                               -p["max_cosine"], p["a_path"], p["b_path"]))
    counter = Counter(p["triage_class"] for p in ranked)
    return {
        "schema_version":"0.1.0",
        "method":"heuristic interpretation of recorded local evidence only",
        "source_revision":report["source_revision"],
        "model":report.get("model"),
        "pairs_retained":len(ranked),
        "candidate_pairs_total":report["candidate_pairs_total"],
        "coverage_limit_note":(
            "Original report may have been truncated to top N candidate pairs; "
            "counts by class describe only analyzed pairs."
        ),
        "counts_by_class":dict(sorted(counter.items())),
        "pairs":ranked,
        "verified":False
    }


def save(report:dict, dest:Path) -> None:
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"semantic_triage.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=[
        "# Evidence-aware semantic triage", "",
        "**All results are unverified, not scientific consensus or deletion advice.**",
        "The original embedding ranking is preserved in semantic.json.", "",
        f"Source: \x60{report['source_revision']}\x60",
        f"Retained: {report['pairs_retained']} / {report['candidate_pairs_total']} candidate pairs.",
        "", "## Categories"
    ]
    for key,value in report["counts_by_class"].items():
        lines.append(f"- \x60{key}\x60: {value}")
    lines.extend(["","## Ranked candidates", ""])
    for idx,pair in enumerate(report["pairs"],1):
        lines.extend([
            f"### {idx}. {pair['a_path']} ↔ {pair['b_path']}",
            f"- Class: \x60{pair['triage_class']}\x60; max cosine: "
            f"{pair['max_cosine']:.3f}; harmonic matched fraction: "
            f"{pair['harmonic_coverage']:.3f}",
            f"- Evidence: {pair['evidence_composition']}; "
            f"numeric claims to validate: {len(pair['numeric_claims_to_verify'])}"
        ])
        for excerpt in pair.get("evidence",[])[:2]:
            lines.append(f"- {excerpt['a_locator']} / {excerpt['b_locator']} "
                         f"({excerpt['score']:.3f})")
        lines.append("")
    (dest/"semantic_triage.md").write_text("\n".join(lines),encoding="utf-8")


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    validate_output_dir(args.root,args.output_dir)
    result=summarize(json.loads(args.input.read_text(encoding="utf-8")))
    save(result,args.output_dir)
    print("SEMANTIC_TRIAGE "+json.dumps({
        "counts":result["counts_by_class"],
        "retained":result["pairs_retained"],
        "total":result["candidate_pairs_total"],
        "verified":False},ensure_ascii=False))
    for item in result["pairs"][:15]:
        print("TRIAGE_PAIR "+json.dumps({
            "a":item["a_path"],"b":item["b_path"],
            "category":item["triage_class"],
            "score":item["max_cosine"],
            "harmonic":item["harmonic_coverage"],
            "numeric_claims":len(item["numeric_claims_to_verify"])
        },ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
