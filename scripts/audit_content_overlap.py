#!/usr/bin/env python3
"""Read-only, evidence-oriented audit of overlap in publicly distributed reports.

Phase 0/1 pilot for MatPomGit/self#138. This deliberately reports candidates,
not semantic equivalence or a verdict that any document should be removed.
No network requests, embeddings, LLMs or remote API calls.
"""
from __future__ import annotations

import argparse
import csv
import io
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

ALLOWED = {".pdf", ".docx", ".odt"}
STOP = set(("i w z na do od po jest sa są aby oraz dla tego tej tym gdy jako które który "
            "być było był czy to nie też the and of to in for with a is are by this "
            "that from or an on using as based").split())
TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
MAX_BYTES = 25 * 1024 * 1024
MAX_PAGES = 300
MAX_CHARACTERS = 700_000
NGRAM = 5
WITNESS_N = 10


def clean(s: str) -> str:
    return " ".join(s.replace("\x00", "").split())


def tokens(s: str) -> list[str]:
    return [t.lower() for t in TOKEN.findall(unicodedata.normalize("NFKC", s))]


def grams(words: list[str], n: int = NGRAM) -> set[tuple[str, ...]]:
    return set(zip(*(words[i:] for i in range(n)))) if len(words) >= n else set()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass
class Extracted:
    path: str
    source_hash: str
    status: str
    segments: list[dict]
    words: list[str]
    warning: str = ""


def pdf_segments(path: Path) -> tuple[list[dict], str]:
    from pypdf import PdfReader
    reader = PdfReader(str(path), strict=False)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDF")
    pages = len(reader.pages)
    output = []
    count = 0
    for i in range(min(pages, MAX_PAGES)):
        content = clean(reader.pages[i].extract_text() or "")
        if content:
            remainder = MAX_CHARACTERS - count
            output.append({"location": f"str. {i+1}", "text": content[:remainder]})
            count += min(len(content), remainder)
        if count >= MAX_CHARACTERS:
            break
    warning = ("LIMIT_PAGES" if pages > MAX_PAGES else
               "LIMIT_CHARS" if count >= MAX_CHARACTERS else "")
    return output, warning


def office_segments(path: Path) -> tuple[list[dict], str]:
    if path.suffix.lower() == ".docx":
        name = "word/document.xml"
        tag = "p"
        p_tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
        text_tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
    else:
        name = "content.xml"
        tag = "p"
        p_tag = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"
        text_tag = None
    with ZipFile(path) as archive:
        info = archive.getinfo(name)
        # Reject compressed XML bombs before expanding potentially huge content.
        if info.file_size > 20 * 1024 * 1024:
            raise ValueError("Office document XML exceeds 20 MiB limit")
        if info.file_size > 1_000_000 and info.file_size > 200 * max(1, info.compress_size):
            raise ValueError("Office document XML compression ratio exceeds limit")
        payload = archive.read(info)
    root = ET.fromstring(payload)
    out = []
    total = 0
    for node in root.iter():
        if node.tag != p_tag:
            continue
        if text_tag:
            value = clean(" ".join(x.text or "" for x in node.iter(text_tag)))
        else:
            value = clean(" ".join(node.itertext()))
        if not value:
            continue
        remaining = MAX_CHARACTERS - total
        out.append({"location": f"akapit {len(out)+1}", "text": value[:remaining]})
        total += min(len(value), remaining)
        if total >= MAX_CHARACTERS:
            break
    return out, ("LIMIT_CHARS" if total >= MAX_CHARACTERS else "")


def extract(path: Path, root: Path) -> Extracted:
    relative = path.relative_to(root).as_posix()
    digest = sha(path)
    if path.stat().st_size > MAX_BYTES:
        return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", [], [], "LIMIT_BYTES")
    try:
        if path.suffix.lower() == ".pdf":
            segments, warning = pdf_segments(path)
        else:
            segments, warning = office_segments(path)
        text = " ".join(segment["text"] for segment in segments)
        words = tokens(text)
        if not words:
            return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", segments, [], "NO_TEXT")
        return Extracted(relative, digest,
                         "EXTRACTION_INCOMPLETE" if warning else "EXTRACTED",
                         segments, words, warning)
    except (OSError, BadZipFile, ValueError, KeyError, ET.ParseError,
            ImportError, IndexError) as exc:
        return Extracted(relative, digest, "EXTRACTION_INCOMPLETE", [], [],
                         f"{type(exc).__name__}: {str(exc)[:80]}")


def doc_key(path: str) -> str:
    filename = Path(path)
    stem = unicodedata.normalize("NFC", filename.stem).casefold()
    return filename.parent.as_posix() + "/" + stem


def common_witness(a: Extracted, b: Extracted) -> list[dict]:
    # Page and paragraph addresses, not claims of semantic equivalence.
    index: dict[tuple[str, ...], tuple[str, str]] = {}
    for seg in a.segments:
        wordlist = tokens(seg["text"])
        for i in range(max(0, len(wordlist) - WITNESS_N + 1)):
            piece = tuple(wordlist[i:i + WITNESS_N])
            index.setdefault(piece, (seg["location"], " ".join(piece)))
    found = []
    seen = set()
    for seg in b.segments:
        wordlist = tokens(seg["text"])
        for i in range(max(0, len(wordlist) - WITNESS_N + 1)):
            piece = tuple(wordlist[i:i + WITNESS_N])
            if piece not in index:
                continue
            first_location, snippet = index[piece]
            if (first_location, seg["location"]) in seen:
                continue
            seen.add((first_location, seg["location"]))
            found.append({"a_location": first_location, "b_location": seg["location"],
                          "shared_text": snippet[:180]})
            if len(found) >= 3:
                return found
    return found


def compute(root: Path, scope: Path) -> dict:
    paths = sorted(
        (p for p in scope.rglob("*") if p.is_file() and not p.is_symlink()
         and p.suffix.lower() in ALLOWED), key=lambda p: p.as_posix().casefold()
    )
    extracted = [extract(p, root) for p in paths]
    by_key = defaultdict(list)
    for item in extracted:
        by_key[doc_key(item.path)].append(item)
    documents = []
    split_variants = set()
    for key, variants in sorted(by_key.items()):
        # Group format exports only if their full-text n-grams do not contradict
        # that assumption. A same-named PDF may be an entirely different report.
        variants.sort(key=lambda x: (x.status != "EXTRACTED",
                                      {".docx": 0, ".odt": 1, ".pdf": 2}.get(
                                          Path(x.path).suffix.lower(), 3), x.path))
        canonical = variants[0]
        canonical_grams = grams(canonical.words)
        grouped = [canonical]
        for variant in variants[1:]:
            g = grams(variant.words)
            shorter = min(len(g), len(canonical_grams))
            coverage = len(g & canonical_grams) / shorter if shorter else None
            if (coverage is not None and coverage < .25
                    and canonical.status == "EXTRACTED"
                    and variant.status == "EXTRACTED"):
                # Distinct logical document until editorial review confirms
                # otherwise. Preserve the original filename-based format group.
                split_variants.add(variant.path)
                documents.append((key + "::" + variant.path.rsplit(".", 1)[-1],
                                  variant, [variant]))
            else:
                grouped.append(variant)
        documents.append((key, canonical, grouped))
    documents.sort(key=lambda group: group[0])
    doc_ids = {item.path: key for key, _, variants in documents for item in variants}
    gram_sets = [grams(doc.words) for _, doc, _ in documents]
    all_words = [Counter(w for w in doc.words if len(w) > 2 and w not in STOP)
                 for _, doc, _ in documents]
    docfreq = Counter(w for counts in all_words for w in counts)
    vectors = []
    norms = []
    total = len(documents)
    for counts in all_words:
        values = {term: (1+math.log(freq)) * math.log(1+(total+1)/(docfreq[term]+1))
                  for term, freq in counts.items()}
        vectors.append(values)
        norms.append(math.sqrt(sum(v*v for v in values.values())))
    pairs = []
    for i, (akey, adoc, avariants) in enumerate(documents):
        for j in range(i+1, len(documents)):
            bkey, bdoc, bvariants = documents[j]
            if not gram_sets[i] or not gram_sets[j]:
                continue
            common = len(gram_sets[i] & gram_sets[j])
            min_g = min(len(gram_sets[i]), len(gram_sets[j]))
            coverage = common / min_g
            union = len(gram_sets[i] | gram_sets[j])
            jaccard = common / union if union else 0
            v1, v2 = vectors[i], vectors[j]
            if len(v1) > len(v2):
                v1, v2 = v2, v1
            dot = sum(val*v2.get(term,0) for term,val in v1.items())
            cosine = dot / (norms[i]*norms[j]) if norms[i]*norms[j] else 0
            # Only lexical candidate discovery; no sentence embeddings or LLMs.
            if coverage < .11 and cosine < .40:
                continue
            witnesses = common_witness(adoc, bdoc) if common >= 2 else []
            pairs.append({
                "a": akey, "b": bkey,
                "a_path": adoc.path, "b_path": bdoc.path,
                "coverage_shorter_5gram": round(coverage,4),
                "jaccard_5gram": round(jaccard,4),
                "tfidf_cosine": round(cosine,4),
                "common_5grams": common,
                "evidence": witnesses,
                "classification": ("NEAR_TEXT_DUPLICATE_CANDIDATE" if coverage >= .65
                                   else "TEXT_OVERLAP_CANDIDATE" if coverage >= .23
                                   else "RELATED_TOPIC_CANDIDATE"),
                "verified": False
            })
    pairs.sort(key=lambda p: (-p["coverage_shorter_5gram"],
                              -p["tfidf_cosine"], p["a"], p["b"]))
    formats = []
    # Report format discrepancies even when low-text-equivalence siblings have
    # been split into separate logical documents for pairwise discovery.
    for key, variants in sorted(by_key.items()):
        if len(variants) < 2:
            continue
        gs = [grams(item.words) for item in variants]
        scores = []
        for i in range(len(variants)):
            for j in range(i+1,len(variants)):
                shorter = min(len(gs[i]),len(gs[j]))
                similarity = len(gs[i] & gs[j]) / shorter if shorter else None
                scores.append({"a": variants[i].path, "b": variants[j].path,
                               "coverage_shorter_5gram": (round(similarity,4)
                                                          if similarity is not None else None),
                               "evidence": common_witness(variants[i], variants[j])
                               if similarity is not None and similarity >= .05 else []})
        formats.append({
            "key": key, "files": [f.path for f in variants],
            "comparisons": scores,
            "status": ("FORMAT_VARIANTS_SPLIT_CANDIDATE"
                       if any(x.path in split_variants for x in variants)
                       else "FORMAT_VARIANTS_UNVERIFIED")
        })
    result = {
        "schema_version": "0.2.0",
        "method": "deterministic lexical comparison, no semantic model; candidates require review",
        "source_revision": revision(root),
        "scope": scope.relative_to(root).as_posix(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "files": len(paths), "logical_documents": len(documents),
            "format_groups": len(formats),
            "split_variants": len(split_variants),
            "extracted": sum(x.status == "EXTRACTED" for x in extracted),
            "extraction_incomplete": sum(x.status != "EXTRACTED" for x in extracted),
            "pairs_flagged": len(pairs),
            "unverified": len(pairs)
        },
        "files": [{"path": x.path, "sha256": x.source_hash, "status": x.status,
                   "warning": x.warning, "word_count": len(x.words),
                   "sections": len(x.segments),
                   "document_id": doc_ids[x.path]} for x in extracted],
        "formats": formats,
        "pairs": pairs
    }
    return result


def revision(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                       stderr=subprocess.DEVNULL, timeout=3,
                                       text=True).strip()
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def validate_output_dir(root: Path, destination: Path) -> None:
    """Never write audit results into directories deployed to GitHub Pages."""
    root = root.resolve()
    destination = destination.resolve()
    for name in ("files", "docs", "materials", "_site"):
        deployed = root / name
        if destination == deployed or destination.is_relative_to(deployed):
            raise ValueError(f"Audit output cannot be inside public directory {name}/")


def audit_manifest(result: dict) -> dict:
    """Deterministic source ledger, independent of wall-clock run time.

    This is not a semantic verification report. All hashes are derived from the
    analyzed bytes and stable source paths; no raw document text is copied here.
    """
    files = sorted(result["files"], key=lambda item: item["path"])
    return {
        "schema_version": "1.0.0",
        "source_revision": result["source_revision"],
        "scope": result["scope"],
        "parameters": {
            "ngram": NGRAM,
            "witness_ngram": WITNESS_N,
            "maximum_file_bytes": MAX_BYTES,
            "maximum_pdf_pages": MAX_PAGES,
            "maximum_characters": MAX_CHARACTERS,
            "allowed_extensions": sorted(ALLOWED),
            "candidate_min_coverage": 0.11,
            "candidate_min_tfidf_cosine": 0.40,
        },
        "counts": result["counts"],
        "sources": [
            {"path": item["path"], "sha256": item["sha256"],
             "logical_document_id": item["document_id"],
             "format": Path(item["path"]).suffix.lower(),
             "extraction_status": item["status"],
             "warning": item["warning"]}
            for item in files
        ],
        "pair_decisions": "UNVERIFIED: candidate discovery only",
    }


PAIR_CSV_FIELDS = (
    "a_document_id", "b_document_id", "a_path", "b_path",
    "classification", "verified", "coverage_shorter_5gram",
    "jaccard_5gram", "tfidf_cosine", "common_5grams",
    "evidence_json",
)


def pair_matrix_csv(result: dict) -> str:
    """Stable, UTF-8 CSV with complete candidate evidence and fixed field order."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=PAIR_CSV_FIELDS,
                            lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for pair in sorted(result["pairs"], key=lambda x: (x["a"], x["b"])):
        writer.writerow({
            "a_document_id": pair["a"],
            "b_document_id": pair["b"],
            "a_path": pair["a_path"],
            "b_path": pair["b_path"],
            "classification": pair["classification"],
            "verified": str(pair["verified"]).lower(),
            "coverage_shorter_5gram": pair["coverage_shorter_5gram"],
            "jaccard_5gram": pair["jaccard_5gram"],
            "tfidf_cosine": pair["tfidf_cosine"],
            "common_5grams": pair["common_5grams"],
            "evidence_json": json.dumps(pair["evidence"], ensure_ascii=False,
                                         sort_keys=True, separators=(",", ":")),
        })
    return output.getvalue()


def write_reports(result: dict, dest: Path, top: int) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "overlap.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dest / "manifest.json").write_text(
        json.dumps(audit_manifest(result), ensure_ascii=False, sort_keys=True,
                   indent=2) + "\n", encoding="utf-8")
    (dest / "matrix.csv").write_text(pair_matrix_csv(result), encoding="utf-8")
    counts = result["counts"]
    lines = [
        "# Content overlap audit — pilot", "",
        f"Source SHA: \`{result['source_revision']}\`  ",
        f"Scope: \`{result['scope']}\`",
        "",
        "## Coverage",
        f"- Files: **{counts['files']}**; logical documents: **{counts['logical_documents']}**.",
        f"- Format-variant groups: **{counts['format_groups']}**; suspicious split variants: **{counts['split_variants']}**.",
        f"- Extracted: **{counts['extracted']}**; incomplete: **{counts['extraction_incomplete']}**.",
        f"- Flagged lexical candidates: **{counts['pairs_flagged']}**.",
        "",
        "**Warning:** similarity is lexical, not a semantic validation or a consolidation decision.",
        "No sources were modified. All candidates below are unverified.", "",
        "## Highest-ranked cross-document candidates", ""
    ]
    if not result["pairs"]:
        lines.append("No lexical candidates passed the discovery thresholds.")
    for n, p in enumerate(result["pairs"][:top], 1):
        a, b = p["a_path"], p["b_path"]
        lines.extend([
            f"### {n}. \`{a}\` vs \`{b}\`",
            f"Classification: \`{p['classification']}\` | coverage (shorter): "
            f"**{p['coverage_shorter_5gram']:.1%}** | TF-IDF cosine: "
            f"**{p['tfidf_cosine']:.3f}** | status: **UNVERIFIED**.",
        ])
        if p["evidence"]:
            lines.append("Matched contiguous wording (locators to be reviewed):")
            for w in p["evidence"]:
                lines.append(f"- {w['a_location']} / {w['b_location']}: "
                             f"“{w['shared_text']}”")
        else:
            lines.append("- No sufficiently long identical passage identified.")
        lines.append("")
    lines.extend(["## Format pairs", ""])
    for group in result["formats"]:
        comparisons = group["comparisons"]
        scores = [x["coverage_shorter_5gram"] for x in comparisons
                  if x["coverage_shorter_5gram"] is not None]
        marker = (f"{min(scores):.1%}" if scores else "unavailable")
        lines.append(f"- \`{group['key']}\` — overlap of shortest text: {marker}. "
                     "Requires editorial equivalence check.")
    lines.extend(["", "## Extraction problems", ""])
    for x in result["files"]:
        if x["status"] != "EXTRACTED":
            lines.append(f"- \`{x['path']}\`: {x['warning'] or 'INCOMPLETE'}")
    lines.extend(["", "## Next steps",
                  "1. Verify leading pairs at indicated sections, retaining unique findings.",
                  "2. Add multilingual embedding retrieval and claim-level evidence before MERGE decisions.",
                  "3. Compare reports against didactic materials separately, with educational context.",
                  ""])
    (dest / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope", default="files/inne/analizy")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--ci-summary", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    scope = (root / args.scope).resolve()
    if not scope.is_relative_to(root) or not scope.is_dir():
        parser.error("--scope must be an existing directory inside repository")
    validate_output_dir(root, args.output_dir)
    report = compute(root, scope)
    write_reports(report, args.output_dir, args.top)
    summary = report["counts"]
    print("CONTENT_AUDIT "+json.dumps(summary, ensure_ascii=False, sort_keys=True))
    for p in report["pairs"][:min(10,args.top)]:
        print("CANDIDATE "+json.dumps({
            "a": p["a_path"], "b": p["b_path"],
            "coverage": p["coverage_shorter_5gram"],
            "cosine": p["tfidf_cosine"], "class": p["classification"],
            "evidence": p["evidence"][:1]
        },ensure_ascii=False))
    # Compare parallel formats separately; log low-confidence equivalence.
    index = {item["path"]: item for item in report["files"]}
    for group in report["formats"]:
        for item in group["comparisons"]:
            score = item["coverage_shorter_5gram"]
            print("FORMAT_PAIR "+json.dumps({
                "a": item["a"], "b": item["b"],
                "coverage": score,
                "a_words": index[item["a"]]["word_count"],
                "b_words": index[item["b"]]["word_count"],
                "needs_review": score is None or score < .75
            }, ensure_ascii=False))
    for p in report["pairs"][:min(10,args.top)]:
        print("CANDIDATE_SIZE "+json.dumps({
            "a": p["a_path"], "b": p["b_path"],
            "a_words": index[p["a_path"]]["word_count"],
            "b_words": index[p["b_path"]]["word_count"],
            "witnesses": len(p["evidence"])
        }, ensure_ascii=False))
    # Diagnostic excerpts are included only for exceptional format variants
    # and the leading candidate pairs, not for the entire corpus.
    exceptional = {item["a"] for group in report["formats"]
                   for item in group["comparisons"]
                   if item["coverage_shorter_5gram"] is None or
                   item["coverage_shorter_5gram"] < .75}
    exceptional |= {item["b"] for group in report["formats"]
                    for item in group["comparisons"]
                    if item["coverage_shorter_5gram"] is None or
                    item["coverage_shorter_5gram"] < .75}
    for pair in report["pairs"][:2]:
        exceptional.add(pair["a_path"])
        exceptional.add(pair["b_path"])
    for name in sorted(exceptional):
        sample = extract(root / name, root)
        first = " ".join(s["text"] for s in sample.segments[:3])
        print("DOCUMENT_PREVIEW " + json.dumps({
            "path": name, "beginning": first[:260], "status": sample.status
        }, ensure_ascii=False))
    if args.ci_summary:
        summary_file = __import__("os").environ.get("GITHUB_STEP_SUMMARY")
        if summary_file:
            with open(summary_file,"a",encoding="utf-8") as output:
                output.write((args.output_dir/"summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
