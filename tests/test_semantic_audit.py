"""Tests for offline multilingual retrieval and synthetic calibration (#138).

A fake encoder exercises orchestration; no real semantic performance is claimed.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile
from xml.sax.saxutils import escape
import importlib.util
import json
import os
import sys
import types
import unittest

import numpy as np

from scripts.audit_content_overlap import Extracted
from scripts.audit_semantic_overlap import (
    analyze, choose_documents, content_windows, load_model_offline,
    model_provenance, score_pairs
)
from scripts.evaluate_semantic_benchmark import evaluate, validate_fixture

ROOT = Path(__file__).resolve().parents[1]


class ControlledEncoder:
    def __init__(self, vectors):
        self.vectors = np.asarray(vectors, dtype="float32")

    def encode(self, texts, **kwargs):
        if len(texts) != len(self.vectors):
            raise AssertionError("Incorrect input count")
        return self.vectors


def docx(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    source = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:body><w:p><w:r><w:t>' + escape(value) +
              '</w:t></w:r></w:p></w:body></w:document>')
    with ZipFile(path,"w") as z:
        z.writestr("word/document.xml",source)


class SemanticAuditTests(unittest.TestCase):
    def test_chunks_preserve_source_locations(self):
        words = " ".join(f"token{i}" for i in range(230))
        d = Extracted("a.docx","1"*64,"EXTRACTED",
                      [{"location":"akapit 3","text":words}],words.split())
        passages = content_windows(d)
        self.assertEqual(len(passages),3)
        self.assertEqual(passages[0]["locator"],"akapit 3, wyrazy od 1")
        self.assertEqual(passages[1]["locator"],"akapit 3, wyrazy od 81")
        self.assertTrue(all(x["source"]=="a.docx" for x in passages))

    def test_format_variants_use_distinct_logical_ids(self):
        inventory={"files":[
            {"path":"a.pdf","document_id":"group","status":"EXTRACTED"},
            {"path":"a.docx","document_id":"group","status":"EXTRACTED"},
            {"path":"b.pdf","document_id":"split::pdf","status":"EXTRACTED"}]}
        docs=choose_documents(inventory)
        self.assertEqual(len(docs),2)
        self.assertEqual(docs[0]["path"],"a.docx")
        self.assertEqual(docs[1]["path"],"b.pdf")

    def test_retrieval_scores_are_addressable_not_duplicate_decisions(self):
        def part(path,locator):
            return {"text":"Przykładowa treść modelu.", "source":path,
                    "locator":locator}
        docs=[
            {"id":"a","source":"a.docx","sha256":"a"*64,
             "passages":[part("a.docx","akapit 1")]},
            {"id":"b","source":"b.pdf","sha256":"b"*64,
             "passages":[part("b.pdf","str. 2")]},
            {"id":"c","source":"c.pdf","sha256":"c"*64,
             "passages":[part("c.pdf","str. 1")]},
        ]
        embeddings=np.asarray([[1,0,0],[.99,.01,0],[0,0,1]],dtype="float32")
        pairs,total=score_pairs(docs,embeddings,threshold=.8)
        self.assertEqual(total,1)
        self.assertEqual(len(pairs),1)
        item=pairs[0]
        self.assertEqual((item["a"],item["b"]),("a","b"))
        self.assertEqual(item["evidence"][0]["a_locator"],"akapit 1")
        self.assertEqual(item["evidence"][0]["b_locator"],"str. 2")
        self.assertFalse(item["verified"])
        self.assertEqual(item["status"],"SEMANTIC_RETRIEVAL_CANDIDATE")

    def test_real_pipeline_uses_fake_encoder_without_network(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            scope=root/"files/inne/analizy"
            phrase=("W badaniu analizowano zależności pomiędzy parametrami "
                    "pomiarowymi a modelowaniem zachowania uczestnika. ")*8
            docx(scope/"Pierwszy.docx",phrase)
            docx(scope/"Drugi.docx",phrase)
            model=ControlledEncoder([[1.,0.],[1.,0.]])
            result=analyze(root,scope,model,threshold=.9,top=10)
            self.assertEqual(result["documents"],2)
            self.assertEqual(result["passages"],2)
            self.assertEqual(result["candidate_pairs_total"],1)
            self.assertFalse(result["pairs"][0]["verified"])
            self.assertEqual(result["extraction_incomplete"],[])

    def test_local_model_is_required_and_no_remote_code_is_allowed(self):
        with TemporaryDirectory() as temp:
            folder=Path(temp)
            with self.assertRaises(ValueError):
                model_provenance(folder)
            (folder/"config.json").write_text('{"id":"test"}',encoding="utf-8")
            seen={}
            module=types.ModuleType("sentence_transformers")
            def fake(name,**kwargs):
                seen.update({"name":name,**kwargs})
                return object()
            module.SentenceTransformer=fake
            with patch.dict(sys.modules,{"sentence_transformers":module}):
                with patch.dict(os.environ,{},clear=False):
                    load_model_offline(folder)
                    self.assertEqual(os.environ["HF_HUB_OFFLINE"],"1")
                    self.assertEqual(os.environ["TRANSFORMERS_OFFLINE"],"1")
            self.assertEqual(seen["name"],str(folder.resolve()))
            self.assertIs(seen["local_files_only"],True)
            self.assertIs(seen["trust_remote_code"],False)

    def test_synthetic_benchmark_labels_are_not_automatic_ground_truth(self):
        fixture=json.loads((ROOT/"tests/fixtures/semantic_pairs.json").read_text(encoding="utf-8"))
        validate_fixture(fixture)
        self.assertGreaterEqual(len(fixture["pairs"]),12)
        negative={x["label"] for x in fixture["pairs"] if x["label"] not in fixture["positive_labels"]}
        self.assertIn("contradiction",negative)
        self.assertIn("related",negative)
        vectors=[]
        for sample in fixture["pairs"]:
            vectors.append([1,0])
            vectors.append([1,0] if sample["label"] in fixture["positive_labels"]
                           else [0,1])
        report=evaluate(ControlledEncoder(vectors),fixture,threshold=.8)
        self.assertEqual(report["confusion"]["fp"],0)
        self.assertEqual(report["confusion"]["fn"],0)
        self.assertEqual(report["precision"],1.)
        self.assertFalse(report["verified_on_real_documents"])


if __name__=="__main__":
    unittest.main()
