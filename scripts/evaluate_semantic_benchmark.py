#!/usr/bin/env python3
"""Evaluate a locally installed semantic encoder on labeled sentence pairs.

This small synthetic smoke benchmark is not evidence of scientific quality
or calibration on the real corpus. Contradictory claims count as negative.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__:
    from .audit_semantic_overlap import load_model_offline, model_provenance
    from .audit_content_overlap import validate_output_dir
else:
    from audit_semantic_overlap import load_model_offline, model_provenance
    from audit_content_overlap import validate_output_dir


def validate_fixture(data):
    if data.get("schema_version") != "0.1.0":
        raise ValueError("Unsupported benchmark schema")
    positive = set(data["positive_labels"])
    if positive != {"same_claim", "paraphrase"}:
        raise ValueError("Positive labels must identify equivalence only")
    ids = set()
    positives, negatives = 0, 0
    for item in data["pairs"]:
        if item["id"] in ids or not item["a"].strip() or not item["b"].strip():
            raise ValueError("Duplicate ID or empty sentence")
        ids.add(item["id"])
        if item["label"] not in positive | {"related", "contradiction", "unrelated"}:
            raise ValueError(f"Unknown label: {item['label']}")
        if item["label"] in positive:
            positives += 1
        else:
            negatives += 1
    if not positives or not negatives:
        raise ValueError("Need both positive and negative pairs")


def evaluate(encoder, data, *, threshold=0.76):
    import numpy as np
    validate_fixture(data)
    if not 0 < threshold <= 1:
        raise ValueError("Threshold must be in (0,1]")
    entries = data["pairs"]
    vectors = np.asarray(encoder.encode(
        [s for item in entries for s in (item["a"],item["b"])],
        batch_size=24, normalize_embeddings=True,
        show_progress_bar=False), dtype="float32")
    if vectors.shape[0] != 2*len(entries):
        raise ValueError("Model returned the wrong number of embeddings")
    norms = np.linalg.norm(vectors, axis=1)
    if not np.isfinite(vectors).all() or (norms < 1e-12).any():
        raise ValueError("Invalid embedding vectors")
    vectors = vectors / norms[:,None]
    similarities = np.sum(vectors[0::2] * vectors[1::2], axis=1)
    tp=fp=tn=fn=0
    samples = []
    positive_labels = set(data["positive_labels"])
    for item, sim in zip(entries, similarities):
        expected = item["label"] in positive_labels
        predicted = float(sim) >= threshold
        if expected and predicted: tp+=1
        elif expected and not predicted: fn+=1
        elif not expected and predicted: fp+=1
        else: tn+=1
        samples.append({"id": item["id"], "label": item["label"],
                        "similarity": round(float(sim),5),
                        "expected_equivalence": expected,
                        "predicted_equivalence": predicted,
                        "correct": expected == predicted})
    precision = tp/(tp+fp) if tp+fp else 0.
    recall = tp/(tp+fn) if tp+fn else 0.
    specificity = tn/(tn+fp) if tn+fp else 0.
    return {"source":"SYNTHETIC_SMOKE_BENCHMARK_ONLY",
            "threshold":threshold, "samples":samples,
            "confusion":{"tp":tp,"fp":fp,"tn":tn,"fn":fn},
            "precision":round(precision,4),"recall":round(recall,4),
            "f1":round(2*precision*recall/(precision+recall),4)
                  if precision+recall else 0.,
            "balanced_accuracy":round((recall+specificity)/2,4),
            "verified_on_real_documents":False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--fixtures", type=Path,
                        default=Path("tests/fixtures/semantic_pairs.json"))
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=.76)
    args = parser.parse_args()
    root = args.root.resolve()
    validate_output_dir(root,args.output_dir)
    fixture = args.fixtures if args.fixtures.is_absolute() else root/args.fixtures
    data = json.loads(fixture.read_text(encoding="utf-8"))
    provenance = model_provenance(args.model_dir)
    model = load_model_offline(args.model_dir)
    report = evaluate(model, data, threshold=args.threshold)
    report["model"] = provenance
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/"semantic_benchmark.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
    print("SYNTHETIC_SEMANTIC_BENCHMARK " + json.dumps({
        "confusion":report["confusion"],"precision":report["precision"],
        "recall":report["recall"],"f1":report["f1"],
        "verified_on_real_documents":False},ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
