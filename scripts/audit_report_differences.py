#!/usr/bin/env python3
"""Pairwise passage audit with evidence for selected reports in self#138.

This is a lexical comparison, NOT a semantic or factual equivalence judgment.
Reports are output only outside public files/, and source files are read-only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import unicodedata

if __package__:
    from .audit_content_overlap import Extracted, extract, revision, tokens, grams, STOP
else:
    from audit_content_overlap import Extracted, extract, revision, tokens, grams, STOP

# Explicit pilot pairs: independently named reports and suspicious format variants.
PAIRS = (
    ("affective-synthesis", "Synteza Modeli multimodalnych.docx",
     "Zautomatyzowana_analiza_afektywna.pdf"),
    ("isaac-lab", "Isaac Lab i bliźniaki cyfrowe.pdf", "Isaac_Lab.docx"),
    ("gesture-slides", "Przewijanie slajdow gestem.docx",
     "Przewijanie slajdow gestem.pdf"),
    ("robots-and-work", "Wpływ robotów na pracę człowieka.docx",
     "Wpływ robotów na pracę człowieka.pdf"),
)
WORD = re.compile(r"\S+")
WINDOW_WORDS = 75
WINDOW_STEP = 55
MATCH_THRESHOLD = 0.64


@dataclass
class Passage:
    location: str
    ordinal: int
    snippet: str
    word_counts: Counter
    char_trigrams: set[str]
    meaningful_words: int


def normalize_chars(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def passages(doc: Extracted, window: int = WINDOW_WORDS,
             step: int = WINDOW_STEP) -> list[Passage]:
    """Evidence-addressable, overlapping short windows within PDF pages/paragraphs."""
    if window < 10 or step < 1:
        raise ValueError("Invalid fragmenting parameters")
    out = []
    for segment in doc.segments:
        raw = segment["text"]
        matches = list(WORD.finditer(raw))
        if not matches:
            continue
        for start in range(0, len(matches), step):
            end = min(len(matches), start + window)
            if end - start < 12 and start > 0:
                break
            phrase = raw[matches[start].start():matches[end - 1].end()]
            words = [x for x in tokens(phrase) if len(x) > 2 and x not in STOP]
            if len(words) < 8:
                continue
            normalized = normalize_chars(phrase)
            trigrams = {normalized[i:i+3] for i in range(max(0, len(normalized) - 2))}
            out.append(Passage(
                location=segment["location"],
                ordinal=start + 1,
                snippet=phrase[:280],
                word_counts=Counter(words),
                char_trigrams=trigrams,
                meaningful_words=len(words)
            ))
            if end == len(matches):
                break
    return out


def score(a: Passage, b: Passage) -> tuple[float, float, float]:
    """Token-frequency cosine and character trigram Jaccard (not embeddings)."""
    common = set(a.word_counts) & set(b.word_counts)
    dot = sum(a.word_counts[w] * b.word_counts[w] for w in common)
    norm_a = math.sqrt(sum(v*v for v in a.word_counts.values()))
    norm_b = math.sqrt(sum(v*v for v in b.word_counts.values()))
    word_cos = dot / (norm_a * norm_b) if norm_a * norm_b else 0.0
    char_union = len(a.char_trigrams | b.char_trigrams)
    char_jac = (len(a.char_trigrams & b.char_trigrams) / char_union
                if char_union else 0.0)
    return round(.72 * word_cos + .28 * char_jac, 5), round(word_cos, 5), round(char_jac, 5)


def locator(p: Passage) -> str:
    return f"{p.location}, wyrazy od {p.ordinal}"


def compare(a: Extracted, b: Extracted, *, label: str,
            same_stem: bool = False, limit: int = 5) -> dict:
    """Rank aligned and possibly unique passages; keep original source locators."""
    left, right = passages(a), passages(b)
    candidate = {
        "id": label, "a": a.path, "b": b.path,
        "a_sha256": a.source_hash, "b_sha256": b.source_hash,
        "a_status": a.status, "b_status": b.status,
        "a_words": len(a.words), "b_words": len(b.words),
        "a_passages": len(left), "b_passages": len(right),
        "method": "TF cosine over tokens + character trigram Jaccard; lexical only",
        "threshold": MATCH_THRESHOLD, "verified": False,
        "interpretation": "REVIEW_REQUIRED",
        "aligned": [], "a_unmatched_candidates": [], "b_unmatched_candidates": [],
    }
    gram_a, gram_b = grams(a.words), grams(b.words)
    shorter = min(len(gram_a), len(gram_b))
    candidate["whole_doc_shorter_5gram_coverage"] = round(
        len(gram_a & gram_b) / shorter, 4) if shorter else None
    if not left or not right:
        candidate["interpretation"] = "EXTRACTION_INCOMPLETE"
        return candidate

    # Best match for every fragment in both directions, including exact locators.
    best_left: list[tuple[float, int, float, float]] = [(0.0, -1, 0.0, 0.0)] * len(left)
    best_right: list[tuple[float, int, float, float]] = [(0.0, -1, 0.0, 0.0)] * len(right)
    for i, one in enumerate(left):
        for j, two in enumerate(right):
            similarity, word_cos, char_jac = score(one, two)
            if similarity > best_left[i][0]:
                best_left[i] = (similarity, j, word_cos, char_jac)
            if similarity > best_right[j][0]:
                best_right[j] = (similarity, i, word_cos, char_jac)

    candidate["a_matched_fraction"] = round(
        sum(v[0] >= MATCH_THRESHOLD for v in best_left) / len(left), 4)
    candidate["b_matched_fraction"] = round(
        sum(v[0] >= MATCH_THRESHOLD for v in best_right) / len(right), 4)
    candidate["mean_best_score_a"] = round(sum(v[0] for v in best_left) / len(left), 4)
    candidate["mean_best_score_b"] = round(sum(v[0] for v in best_right) / len(right), 4)

    aligned = sorted(enumerate(best_left), key=lambda x: (-x[1][0], x[0]))
    selected_locations = set()
    for i, (value, j, word_cos, char_jac) in aligned:
        if value < MATCH_THRESHOLD:
            break
        pair_loc = (left[i].location, right[j].location)
        if pair_loc in selected_locations:
            continue
        selected_locations.add(pair_loc)
        candidate["aligned"].append({
            "similarity": value, "word_cos": word_cos, "char_jaccard": char_jac,
            "a_locator": locator(left[i]), "b_locator": locator(right[j]),
            "a_excerpt": left[i].snippet[:220], "b_excerpt": right[j].snippet[:220]
        })
        if len(candidate["aligned"]) >= limit:
            break

    for side, chunks, best in (
        ("a", left, best_left), ("b", right, best_right)
    ):
        # Evidence of a low-similarity passage, not a determination of uniqueness.
        unmatched = sorted(
            ((i, v[0]) for i, v in enumerate(best) if v[0] < MATCH_THRESHOLD),
            key=lambda x: (x[1], -chunks[x[0]].meaningful_words, x[0])
        )
        found_locations = set()
        for i, value in unmatched:
            if chunks[i].location in found_locations:
                continue
            found_locations.add(chunks[i].location)
            candidate[f"{side}_unmatched_candidates"].append({
                "best_similarity": value,
                "locator": locator(chunks[i]),
                "excerpt": chunks[i].snippet[:260]
            })
            if len(candidate[f"{side}_unmatched_candidates"]) >= limit:
                break

    # These are triage flags, explicitly not editorial consolidation decisions.
    if a.status != "EXTRACTED" or b.status != "EXTRACTED":
        candidate["interpretation"] = "EXTRACTION_INCOMPLETE"
    elif (same_stem and
          candidate["whole_doc_shorter_5gram_coverage"] is not None and
          candidate["whole_doc_shorter_5gram_coverage"] < .25 and
          min(candidate["a_matched_fraction"], candidate["b_matched_fraction"]) < .35):
        candidate["interpretation"] = "FORMAT_VERSION_MISMATCH_CANDIDATE"
    elif not same_stem and min(candidate["a_matched_fraction"],
                               candidate["b_matched_fraction"]) >= .60:
        candidate["interpretation"] = "EXTENSIVE_TEXTUAL_REUSE_CANDIDATE"
    return candidate


def analyze(root: Path, scope: Path, pair_definitions=PAIRS) -> dict:
    results = []
    for label, a_name, b_name in pair_definitions:
        pa, pb = scope / a_name, scope / b_name
        if not pa.is_file() or not pb.is_file():
            results.append({"id": label, "a": a_name, "b": b_name,
                            "interpretation": "MISSING_INPUT", "verified": False})
            continue
        first, second = extract(pa, root), extract(pb, root)
        results.append(compare(first, second, label=label,
                               same_stem=pa.stem.casefold() == pb.stem.casefold()))
    return {
        "schema_version": "0.2.0", "source_revision": revision(root),
        "scope": scope.relative_to(root).as_posix(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "pairs": results
    }


def save(result: dict, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "comparison.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Pilot — detailed report differences", "",
        f"Source SHA: {result['source_revision']}",
        "**Status: all interpretations are unverified lexical indicators.**",
        "No file was removed or modified. Potentially unmatched passages may be",
        "paraphrases or extraction artifacts, not necessarily unique findings.", ""
    ]
    for pair in result["pairs"]:
        lines.extend([
            f"## {pair['id']}",
            f"- A: {pair['a']}",
            f"- B: {pair['b']}",
            f"- Preliminary classification: {pair['interpretation']}",
        ])
        if "a_matched_fraction" not in pair:
            lines.extend(["- Unable to calculate passage similarity.", ""])
            continue
        lines.extend([
            f"- Words: {pair['a_words']} / {pair['b_words']}; "
            f"passage windows: {pair['a_passages']} / {pair['b_passages']}.",
            f"- Matched passage fractions A/B: "
            f"{pair['a_matched_fraction']:.1%} / {pair['b_matched_fraction']:.1%} "
            f"(threshold: {pair['threshold']}).",
            f"- Whole-text 5-gram coverage (shorter): {pair['whole_doc_shorter_5gram_coverage']}.",
            "- Matched excerpts (potential reuse):"
        ])
        for evidence in pair["aligned"]:
            lines.append(f"  - {evidence['a_locator']} ↔ {evidence['b_locator']}"
                         f" (lexical score {evidence['similarity']:.3f})")
            lines.append(f"    - A: “{evidence['a_excerpt']}”")
            lines.append(f"    - B: “{evidence['b_excerpt']}”")
        if not pair["aligned"]:
            lines.append("  - No high lexical-similarity passages passed the threshold.")
        for side in ("a", "b"):
            lines.append(f"- {side.upper()}: low-similarity passages to investigate:")
            for item in pair[f"{side}_unmatched_candidates"]:
                lines.append(f"  - {item['locator']} "
                             f"(best lexical score {item['best_similarity']:.3f}): "
                             f"“{item['excerpt']}”")
            if not pair[f"{side}_unmatched_candidates"]:
                lines.append("  - No unmatched passage candidates.")
        lines.append("")
    (dest / "comparison.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope", default="files/inne/analizy")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ci-summary", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    scope = (root / args.scope).resolve()
    if not scope.is_relative_to(root) or not scope.is_dir():
        parser.error("scope must be a directory within the repository")
    result = analyze(root, scope)
    save(result, args.output_dir)
    for pair in result["pairs"]:
        print("DIFFERENCE_AUDIT " + json.dumps({
            "id": pair["id"], "status": pair["interpretation"],
            "a": pair["a"], "b": pair["b"],
            "fraction_a": pair.get("a_matched_fraction"),
            "fraction_b": pair.get("b_matched_fraction"),
            "whole_5gram": pair.get("whole_doc_shorter_5gram_coverage"),
            "matched_examples": [
                {"a": x["a_locator"], "b": x["b_locator"],
                 "similarity": x["similarity"]}
                for x in pair.get("aligned", [])[:2]],
            "unmatched_a": pair.get("a_unmatched_candidates", [])[:2],
            "unmatched_b": pair.get("b_unmatched_candidates", [])[:2]
        }, ensure_ascii=False))
    if args.ci_summary and os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fd:
            fd.write("\n" + (args.output_dir / "comparison.md").read_text(encoding="utf-8"))
    return 0 if all(p["interpretation"] != "MISSING_INPUT"
                    for p in result["pairs"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
