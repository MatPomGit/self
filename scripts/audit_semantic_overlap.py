#!/usr/bin/env python3
"""Optional, fully OFFLINE multilingual semantic candidate retrieval (self#138).

No model is downloaded, no document is sent to a remote inference service.
Only local model directories are accepted. Results are retrieval hypotheses,
not evidence that any findings, conclusions or citations are equivalent.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

try:
    from .audit_content_overlap import compute, extract, revision, validate_output_dir
except ImportError:
    from audit_content_overlap import compute, extract, revision, validate_output_dir

DEFAULT_THRESHOLD = 0.76  # Candidate discovery only, NOT calibrated accuracy.
CHUNK_WORDS = 100
CHUNK_STEP = 80
MAX_WINDOWS_PER_DOCUMENT = 180


def content_windows(document, *, size=CHUNK_WORDS, step=CHUNK_STEP):
    """Build addressable passages without joining different source pages."""
    if size < 20 or step < 1:
        raise ValueError("Invalid window size/step")
    result = []
    for segment in document.segments:
        text = segment["text"]
        spans = list(re.finditer(r"\S+", text))
        for start in range(0, len(spans), step):
            end = min(start + size, len(spans))
            if end - start < 20:
                break
            excerpt = text[spans[start].start():spans[end-1].end()]
            result.append({
                "locator": f"{segment['location']}, wyrazy od {start+1}",
                "text": excerpt, "source": document.path
            })
            if len(result) >= MAX_WINDOWS_PER_DOCUMENT:
                return result
            if end == len(spans):
                break
    return result


def choose_documents(inventory):
    """One representative per logical document, including split format variants."""
    grouped = defaultdict(list)
    for item in inventory["files"]:
        grouped[item["document_id"]].append(item)
    priorities = {".docx": 0, ".odt": 1, ".pdf": 2}
    chosen = []
    for key, variants in sorted(grouped.items()):
        variants.sort(key=lambda x: (
            x["status"] != "EXTRACTED",
            priorities.get(Path(x["path"]).suffix.lower(), 99),
            x["path"]))
        chosen.append({"id": key, **variants[0]})
    return chosen


def l2normalize(vectors):
    """Normalize vectors, including deterministic fake encoders used in tests."""
    import numpy as np
    values = np.asarray(vectors, dtype="float32")
    if values.ndim != 2 or not len(values) or not values.shape[1]:
        raise ValueError("Encoder must return a nonempty 2D matrix")
    if not np.isfinite(values).all():
        raise ValueError("Encoder returned nonfinite values")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if (norms <= 1e-12).any():
        raise ValueError("Encoder returned a zero vector")
    return values / norms


def score_pairs(documents, vectors, *, threshold=DEFAULT_THRESHOLD, top=30):
    """All document pairs; for each pair retrieve best local passage matches."""
    import numpy as np
    if not 0 < threshold <= 1:
        raise ValueError("Threshold must be within (0, 1]")
    vectors = l2normalize(vectors)
    positions = {}
    passages = []
    for document in documents:
        start = len(passages)
        passages.extend(document["passages"])
        positions[document["id"]] = (start, len(passages))
    if len(passages) != len(vectors):
        raise ValueError("Embedding count does not match source passages")
    pairs = []
    for i, left in enumerate(documents):
        l0, l1 = positions[left["id"]]
        if l0 == l1:
            continue
        for right in documents[i+1:]:
            r0, r1 = positions[right["id"]]
            if r0 == r1:
                continue
            similarity = vectors[l0:l1] @ vectors[r0:r1].T
            best_left = similarity.max(axis=1)
            best_right = similarity.max(axis=0)
            highest = float(similarity.max())
            if highest < threshold:
                continue
            candidates = np.argwhere(similarity >= threshold)
            # Each cited example must use two independent source passages.
            candidate_rows = sorted(
                ((float(similarity[a, b]), int(a), int(b)) for a,b in candidates),
                key=lambda row: (-row[0], row[1], row[2])
            )
            evidence = []
            locations = set()
            for score, a, b in candidate_rows:
                a_location = left["passages"][a]["locator"]
                b_location = right["passages"][b]["locator"]
                pair_key = (a_location, b_location)
                if pair_key in locations:
                    continue
                locations.add(pair_key)
                evidence.append({
                    "score": round(score, 5),
                    "a_locator": a_location,
                    "b_locator": b_location,
                    "a_excerpt": left["passages"][a]["text"][:220],
                    "b_excerpt": right["passages"][b]["text"][:220]
                })
                if len(evidence) >= 4:
                    break
            pairs.append({
                "a": left["id"], "b": right["id"],
                "a_path": left["source"], "b_path": right["source"],
                "a_sha256": left["sha256"], "b_sha256": right["sha256"],
                "max_cosine": round(highest, 5),
                "matched_fraction_a": round(float((best_left >= threshold).mean()), 4),
                "matched_fraction_b": round(float((best_right >= threshold).mean()), 4),
                "evidence": evidence,
                "status": "SEMANTIC_RETRIEVAL_CANDIDATE",
                "verified": False,
            })
    pairs.sort(key=lambda p: (-p["max_cosine"], p["a"], p["b"]))
    return pairs[:top], len(pairs)


def model_provenance(model_dir):
    """Hash the local model configuration, not its large weight files."""
    root = Path(model_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Model directory not found: {root}")
    configs = []
    for name in ("config.json", "modules.json", "sentence_bert_config.json"):
        p = root / name
        if p.is_file():
            configs.append({"name": name,
                            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    if not configs:
        raise ValueError("No model configuration files found")
    return {"local_path": str(root), "configuration_files": configs}


def load_model_offline(model_dir):
    root = Path(model_dir).resolve()
    model_provenance(root)
    # Fail closed: never allow remote weights, metadata checks or code.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Install sentence-transformers on the offline worker first") from exc
    return SentenceTransformer(str(root), local_files_only=True,
                               trust_remote_code=False, device="cpu")


def analyze(root, scope, encoder, *, threshold=DEFAULT_THRESHOLD, top=30):
    inventory = compute(root, scope)
    chosen = choose_documents(inventory)
    documents = []
    for item in chosen:
        source = extract(root/item["path"], root)
        chunks = content_windows(source)
        documents.append({
            "id": item["id"], "source": item["path"],
            "sha256": source.source_hash, "passages": chunks,
            "status": source.status
        })
    texts = [p["text"] for d in documents for p in d["passages"]]
    if not texts:
        raise ValueError("No extractable passages for semantic comparison")
    vectors = encoder.encode(texts, batch_size=24,
                             normalize_embeddings=True,
                             show_progress_bar=False)
    pairs, found = score_pairs(documents, vectors,
                              threshold=threshold, top=top)
    return {
        "schema_version": "0.1.0",
        "scope": scope.relative_to(root).as_posix(),
        "source_revision": revision(root),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "method": "offline multilingual sentence embedding cosine; candidate retrieval only",
        "threshold": threshold,
        "documents": len(documents),
        "passages": len(texts),
        "candidate_pairs_total": found,
        "pairs": pairs,
        "extraction_incomplete": [d["source"] for d in documents
                                  if d["status"] != "EXTRACTED"],
        "verified": False
    }


def save(result, dest):
    dest.mkdir(parents=True, exist_ok=True)
    (dest/"semantic.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Offline semantic candidate audit", "",
        f"Source commit: \x60{result['source_revision']}\x60",
        f"Model: \x60{result['model']['local_path']}\x60",
        f"Documents: {result['documents']} | passages: {result['passages']} "
        f"| candidate pairs: {result['candidate_pairs_total']}",
        "",
        "**Not a consolidation decision:** semantic similarity cannot establish",
        "equivalence of scientific claims, methods or sources. All records are UNVERIFIED.",
        ""
    ]
    for i, pair in enumerate(result["pairs"], 1):
        lines.extend([
            f"## {i}. {pair['a_path']} ↔ {pair['b_path']}",
            f"- Max embedding cosine: {pair['max_cosine']:.3f}",
            f"- Matching passages A/B: "
            f"{pair['matched_fraction_a']:.1%} / {pair['matched_fraction_b']:.1%}",
        ])
        for sample in pair["evidence"][:3]:
            lines.append(f"- {sample['a_locator']} ↔ {sample['b_locator']}: "
                         f"{sample['score']:.3f}")
        lines.append("")
    (dest/"semantic.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope", default="files/inne/analizy")
    parser.add_argument("--model-dir", type=Path, required=True,
                        help="Local directory containing an already-installed model")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--top", type=int, default=30)
    options = parser.parse_args()
    root = options.root.resolve()
    scope = (root/options.scope).resolve()
    if not scope.is_dir() or not scope.is_relative_to(root):
        parser.error("Scope must be an existing directory inside the repository")
    validate_output_dir(root, options.output_dir)
    provenance = model_provenance(options.model_dir)
    encoder = load_model_offline(options.model_dir)
    result = analyze(root, scope, encoder,
                     threshold=options.threshold, top=options.top)
    result["model"] = provenance
    save(result, options.output_dir)
    print("SEMANTIC_AUDIT " + json.dumps({
        "documents": result["documents"],
        "passages": result["passages"],
        "candidates": result["candidate_pairs_total"],
        "model_config": provenance["configuration_files"],
        "verified": False
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
