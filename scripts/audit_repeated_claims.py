#!/usr/bin/env python3
"""Evidence ledger for repeated claims and potentially distinct report sections.

Read-only analysis for self#138. Source-document excerpts are provenance,
NOT independently verified scientific findings. Clinical assessments in
docs/CONTENT_AUDIT_CLAIMS.md rely on separately reviewed literature.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from collections import Counter
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

try:
    from .audit_content_overlap import extract, grams, tokens, revision, validate_output_dir
    from .audit_semantic_overlap import content_windows
except ImportError:
    from audit_content_overlap import extract, grams, tokens, revision, validate_output_dir
    from audit_semantic_overlap import content_windows

REPORTS = {
    "ear_diagnostic_inference": {
        "files": ("Mediapipe.docx", "VGG-Transformer.docx"),
        "terms": (r"\bEAR\b", r"mrugni\w+", r"lęk\w*|depres\w*"),
        "review": "UNSUPPORTED_CLINICAL_THRESHOLD_CANDIDATE",
        "source": "https://fel.cvut.cz/en/faculty/people/444-jan-cech/publications",
    },
    "adhd_asd_rf_performance": {
        "files": ("tele_ndd.docx", "teled_ndd.docx"),
        "terms": (r"\b84\s*%", r"\b86\s*%", r"Random\s*Forest|las\s+losow\w*"),
        "review": "VALID_RESULT_REQUIRES_VALIDATION_CONTEXT",
        "source": "https://doi.org/10.2196/54577",
    },
}
UNIQUE_PAIR = ("Synteza Modeli multimodalnych.docx",
               "Zautomatyzowana_analiza_afektywna.pdf")
MIN_WINDOW_WORDS = 25


def claim_candidates(document, patterns, limit=8):
    compiled = [re.compile(p,re.IGNORECASE) for p in patterns]
    matches = []
    for section in document.segments:
        content = section["text"]
        hits = [rx.search(content) for rx in compiled]
        score = sum(x is not None for x in hits)
        if not score:
            continue
        anchor = min(m.start() for m in hits if m is not None)
        start = max(0, anchor - 120)
        end = min(len(content), anchor + 580)
        excerpt = content[start:end].strip()
        matches.append({
            "locator":section["location"],
            "matching_patterns":score,
            "excerpt":excerpt,
            "possible_truncation":bool(start or end < len(content)),
        })
    matches.sort(key=lambda m:(-m["matching_patterns"],m["locator"]))
    return matches[:limit]


def docx_tables(path):
    """Retain table row boundaries where PDF extraction loses tabular structure."""
    if path.suffix.lower() != ".docx":
        return []
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with ZipFile(path) as archive:
        part = archive.getinfo("word/document.xml")
        if part.file_size > 20*1024*1024:
            raise ValueError("DOCX XML exceeds limit")
        xml = archive.read(part)
    doc = ET.fromstring(xml)
    rows = []
    for table_idx, table in enumerate(doc.iter(namespace+"tbl"),1):
        for row_idx, row in enumerate(table.findall(namespace+"tr"),1):
            texts = []
            for cell in row.findall(namespace+"tc"):
                texts.append(" ".join(
                    element.text or "" for element in cell.iter(namespace+"t")
                ).strip())
            if not any(texts):
                continue
            rows.append({
                "locator":f"tabela {table_idx}, wiersz {row_idx}",
                "cells":texts[:18],
            })
            if len(rows) >= 250:
                return rows
    return rows


def distinct_passages(a,b,limit=10):
    """N-gram evidence for potentially distinct wording, not unique knowledge."""
    target=grams(b.words)
    rows=[]
    for p in content_windows(a):
        w=tokens(p["text"])
        if len(w)<MIN_WINDOW_WORDS:
            continue
        needle=grams(w)
        if not needle:
            continue
        fraction=len(needle & target)/len(needle) if target else 0.
        if fraction >= .8:
            continue  # Already textually well represented in the other report.
        rows.append({
            "source":a.path,"locator":p["locator"],
            "fraction_5gram_found_in_other":round(fraction,4),
            "excerpt":p["text"][:350],
            "verified_unique":False,
        })
    rows.sort(key=lambda x:(x["fraction_5gram_found_in_other"],x["locator"]))
    return rows[:limit]


def table_row_metrics(rowtext, target_grams, target_words):
    """Compare word sets as a layout-tolerant complement to ordered 5-grams."""
    words=tokens(rowtext)
    g=grams(words)
    if len(g)<3:
        return None
    five=len(g & target_grams)/len(g) if target_grams else 0.
    meaningful={w for w in words if len(w)>2}
    shared=len(meaningful & target_words)/len(meaningful) if meaningful else 0.
    if five < .3 and shared >= .75:
        flag="LAYOUT_REORDERING_POSSIBLE"
    elif five < .5 and shared < .6:
        flag="POTENTIALLY_DISTINCT_ROW_WORDING"
    else:
        flag="OVERLAPPING_ROW_CONTENT"
    return {
        "fraction_5gram_found_in_pdf":round(five,4),
        "fraction_words_found_in_pdf":round(shared,4),
        "triage_flag":flag,
    }


def analyze(root,scope):
    findings=[]
    cache={}
    def load(filename):
        if filename not in cache:
            path=scope/filename
            if not path.is_file() or path.is_symlink():
                raise FileNotFoundError(f"Missing report: {path}")
            cache[filename]=extract(path,root)
        return cache[filename]

    for claim_id, spec in REPORTS.items():
        documents=[]
        for filename in spec["files"]:
            doc=load(filename)
            examples=claim_candidates(doc,spec["terms"])
            documents.append({
                "path":doc.path,"sha256":doc.source_hash,
                "status":doc.status,"match_count":len(examples),
                "examples":examples,
            })
        findings.append({
            "id":claim_id,"review_status":spec["review"],
            "reference_url":spec["source"],
            "reviewed_externally":False,
            "documents":documents,
        })

    a=load(UNIQUE_PAIR[0]);b=load(UNIQUE_PAIR[1])
    tables=docx_tables(scope/UNIQUE_PAIR[0])
    comparative=grams(b.words)
    comparative_words=set(b.words)
    table_rows=[]
    for row in tables:
        rowtext=" ".join(row["cells"])
        scores=table_row_metrics(rowtext,comparative,comparative_words)
        if scores is None:
            continue
        table_rows.append({
            **row,**scores,
            "verified_unique":False,
        })
    table_rows.sort(key=lambda x:(x["fraction_5gram_found_in_pdf"],x["locator"]))
    return {
        "schema_version":"0.1.0",
        "source_revision":revision(root),
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "method":"source evidence extraction and 5-gram candidate selection; NOT factual verification",
        "claims":findings,
        "affective_comparison":{
            "a":{"path":a.path,"sha256":a.source_hash,"status":a.status},
            "b":{"path":b.path,"sha256":b.source_hash,"status":b.status},
            "a_distinct_wording_candidates":distinct_passages(a,b),
            "b_distinct_wording_candidates":distinct_passages(b,a),
            "docx_table_rows":len(tables),
            "table_rows_needing_check":table_rows[:12],
            "pdf_table_reconstruction_reliable":False,
        },
        "source_files_modified":False
    }


def save(report,dest):
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"claim_evidence.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=[
        "# Evidence ledger — scientific claim audit", "",
        f"Source commit: \x60{report['source_revision']}\x60",
        "This report extracts source fragments; external scientific conclusions",
        "are documented separately in docs/CONTENT_AUDIT_CLAIMS.md.", "",
    ]
    for item in report["claims"]:
        lines.extend([f"## {item['id']}",
                      f"- Review flag: \x60{item['review_status']}\x60",
                      f"- Primary external source: {item['reference_url']}"])
        for doc in item["documents"]:
            lines.append(f"- \x60{doc['path']}\x60 — "
                         f"{doc['match_count']} candidate source section(s), "
                         f"SHA-256 \x60{doc['sha256']}\x60")
            for example in doc["examples"][:3]:
                lines.append(f"  - {example['locator']} "
                             f"({example['matching_patterns']} patterns): "
                             f"“{example['excerpt'][:250]}”")
    unique=report["affective_comparison"]
    lines.extend(["","## Affective-analysis pair: potentially distinct wording",
                  f"- A: \x60{unique['a']['path']}\x60",
                  f"- B: \x60{unique['b']['path']}\x60",
                  f"- DOCX table rows (extracted): {unique['docx_table_rows']}",
                  "**Warning:** lexical difference does not prove independent scientific",
                  "information. PDF tables are not reliably reconstructed.", ""])
    for key in ("a_distinct_wording_candidates","b_distinct_wording_candidates"):
        lines.append(f"### {key}")
        for x in unique[key][:8]:
            lines.append(f"- {x['locator']} (5-gram coverage in other:"
                         f" {x['fraction_5gram_found_in_other']:.1%}) — "
                         f"“{x['excerpt'][:190]}”")
    lines.append("### Table-row candidates")
    for x in unique["table_rows_needing_check"][:8]:
        lines.append(f"- {x['locator']} (5-gram: "
                     f"{x['fraction_5gram_found_in_pdf']:.1%}; "
                     f"word coverage: {x['fraction_words_found_in_pdf']:.1%}; "
                     f"flag: {x['triage_flag']}) — "
                     f"{' | '.join(x['cells'])[:190]}")
    (dest/"claim_evidence.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope",default="files/inne/analizy")
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    root=args.root.resolve();scope=(root/args.scope).resolve()
    if not scope.is_relative_to(root) or not scope.is_dir():
        parser.error("--scope must be an existing repo subdirectory")
    validate_output_dir(root,args.output_dir)
    report=analyze(root,scope)
    save(report,args.output_dir)
    for claim in report["claims"]:
        print("CLAIM_SIGNAL "+json.dumps({
            "id":claim["id"],"flag":claim["review_status"],
            "files":[{"path":x["path"],"matches":x["match_count"],
                      "top_locator":x["examples"][0]["locator"] if x["examples"] else None}
                     for x in claim["documents"]]
        },ensure_ascii=False))
    a=report["affective_comparison"]
    print("AFFECTIVE_CONTRAST "+json.dumps({
        "a_sections":len(a["a_distinct_wording_candidates"]),
        "b_sections":len(a["b_distinct_wording_candidates"]),
        "docx_table_rows":a["docx_table_rows"],
        "candidate_table_rows":len(a["table_rows_needing_check"]),
        "top_a":a["a_distinct_wording_candidates"][:3],
        "top_b":a["b_distinct_wording_candidates"][:3]
    },ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
