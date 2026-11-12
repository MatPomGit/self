#!/usr/bin/env python3
"""Compare PDF↔DOCX variants, preserving discrepancies as review evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

try:
    from scripts.audit_content_overlap import extract, grams, common_witness, validate_output_dir
    from scripts.audit_material_variants import inventory
except ModuleNotFoundError:
    from audit_content_overlap import extract, grams, common_witness, validate_output_dir
    from audit_material_variants import inventory


def compare(root: Path, candidates: list[dict]) -> dict:
    rows = []
    cache = {}
    for candidate in candidates:
        if candidate["family"] != "pdf_docx":
            continue
        paths = sorted(candidate["files"])
        records = []
        for name in paths:
            if name not in cache:
                path = root / name
                if path.is_symlink() or not path.is_file():
                    continue
                cache[name] = extract(path, root)
            records.append(cache[name])
        if len(records) != 2:
            rows.append({"files": paths, "status": "MISSING_INPUT", "decision": "REVIEW_REQUIRED"})
            continue
        a,b = records
        ga,gb = grams(a.words), grams(b.words)
        common = ga & gb
        coverage = len(common)/min(len(ga),len(gb)) if min(len(ga),len(gb)) else None
        if a.status != "EXTRACTED" or b.status != "EXTRACTED":
            status = "EXTRACTION_INCOMPLETE"
        elif coverage is None:
            status = "INSUFFICIENT_TEXT"
        elif coverage < .25:
            status = "FORMAT_MISMATCH_CANDIDATE"
        elif coverage < .75:
            status = "FORMAT_DIFFERENCE_REVIEW"
        else:
            status = "TEXT_VARIANTS_SIMILAR"
        rows.append({
            "files": paths, "status": status, "decision": "REVIEW_REQUIRED",
            "a_sha256": a.source_hash, "b_sha256": b.source_hash,
            "a_words":len(a.words), "b_words":len(b.words),
            "a_extract_status":a.status, "b_extract_status":b.status,
            "coverage_shorter_5gram":round(coverage,4) if coverage is not None else None,
            "coverage_a":round(len(common)/len(ga),4) if ga else None,
            "coverage_b":round(len(common)/len(gb),4) if gb else None,
            "evidence":common_witness(a,b) if common else [],
        })
    rows.sort(key=lambda p: (p.get("coverage_shorter_5gram") is None,
                              p.get("coverage_shorter_5gram") or 0,p["files"]))
    return {"schema_version":"1.0.0", "scope":"files/", "pairs": rows,
            "method":"lexical 5-gram coverage; no semantic equivalence",
            "limitations":["PDF tables and graphics may be under-extracted",
                           "Shared boilerplate may inflate overlap",
                           "Do not archive source variants without editorial review"]}


def as_md(report:dict) -> str:
    lines=["# PDF–DOCX format comparison","",
           "| Files | Shorter 5-gram coverage | Status |",
           "| --- | ---: | --- |"]
    for p in report["pairs"]:
        score=p.get("coverage_shorter_5gram")
        val=f"{score:.1%}" if score is not None else "n/a"
        name=" / ".join("`"+Path(f).name+"`" for f in p["files"])
        lines.append(f"| {name} | {val} | {p['status']} |")
    lines.extend(["","All decisions require human/editorial review."])
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path("files"))
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    root=args.root.resolve()
    out=args.output_dir.resolve()
    if not root.is_dir():
        parser.error("Input root does not exist")
    validate_output_dir(root.parent,out)
    report=compare(root, inventory(root)["format_variants"])
    out.mkdir(parents=True,exist_ok=True)
    (out/"format_comparison.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"format_comparison.md").write_text(as_md(report),encoding="utf-8")
    print("Compared PDF-DOCX pairs:",len(report["pairs"]))
    from collections import Counter
    print("Statuses:",dict(Counter(p["status"] for p in report["pairs"])))


if __name__=="__main__":
    main()
