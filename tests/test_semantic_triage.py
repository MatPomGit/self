"""Evidence-aware triage tests for semantic retrieval output (#138)."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.triage_semantic_results import (
    classify, is_reference, save, summarize
)


def make_pair(a=0.2,b=0.2,examples=None,score=.95,names=("a.docx","b.pdf")):
    return {
        "a_path":names[0], "b_path":names[1],
        "max_cosine":score,
        "matched_fraction_a":a, "matched_fraction_b":b,
        "evidence":examples or [],
        "verified":False
    }


def sample(a,b,score=.91):
    return {"a_locator":"akapit 4", "b_locator":"str. 3",
            "a_excerpt":a,"b_excerpt":b,"score":score}


class SemanticTriageTests(unittest.TestCase):
    def test_reference_heuristic(self):
        self.assertTrue(is_reference(
            "[4] A. Researcher, Tracking gaze; doi:10.1000/abcd.2023.987"))
        self.assertTrue(is_reference(
            "Bibliografia [1] Przykładowe badanie z 2024 roku"))
        self.assertFalse(is_reference(
            "Badanie wskazuje, że fiksacje mogą wzrastać podczas wysiłku."))
        self.assertFalse(is_reference(
            "Zmienna x>20 ms była wielkością progową w teście."))

    def test_repeated_numeric_claim_not_classed_as_bibliography(self):
        a=("EAR (Eye Aspect Ratio): lęk przy >20 mrugnięć/min "
           "i zmęczenie przy EAR <0,2 przez 0,5 s.")
        b=("Wskaźnik EAR: marker lęku przy >20/min "
           "lub zmęczenia przy EAR <0,2 przez 0,5 s.")
        result=classify(make_pair(.14,.21,[sample(a,b)]))
        self.assertEqual(result["triage_class"],
                         "LOCAL_CONTENT_OVERLAP_CANDIDATE")
        self.assertEqual(len(result["numeric_claims_to_verify"]),1)
        self.assertFalse(result["verified"])

    def test_bibliography_only_pair_downranked(self):
        a="[4] A. Researcher. Gaze Tracking. doi:10.1145/1234.5678."
        b="[4] A Researcher. Gaze Tracking; doi:10.1145/1234.5678."
        result=classify(make_pair(.16,.12,[sample(a,b)]))
        self.assertEqual(result["triage_class"],
                         "SHARED_BIBLIOGRAPHY_CANDIDATE")
        self.assertEqual(result["ranking_tier"],3)

    def test_bibliography_dominates_mixed_source_evidence(self):
        reference=sample(
            "[4] Arakawa, RGBDGaze. DOI:10.1145/3536221.3556568.",
            "[4] Arakawa, RGBDGaze. doi:10.1145/3536221.3556568.")
        narrative=sample("Wyniki badań okulograficznych zależą od próbki.",
                         "W eksperymencie zmieniono protokół oceny spojrzenia.")
        result=classify(make_pair(.16,.12,[reference,reference,narrative]))
        self.assertEqual(result["triage_class"],
                         "BIBLIOGRAPHY_DOMINANT_CANDIDATE")
        self.assertEqual(result["evidence_composition"]["shared_references"],2)

    def test_percentages_are_marked_for_verification(self):
        evidence=sample(
            "Dokładność modelu 84% w warunkach testowych.",
            "Trafność wyniosła 86% dla ASD w tym badaniu.")
        result=classify(make_pair(.2,.2,[evidence]))
        self.assertEqual(len(result["numeric_claims_to_verify"]),1)

    def test_keywords_are_not_report_overlap(self):
        a="Słowa kluczowe: robot humanoidalny, model, ROS2, fuzja."
        b="Słowa kluczowe: robot humanoidalny, ROS2, lokalne modele."
        result=classify(make_pair(.02,.03,[sample(a,b)]))
        self.assertEqual(result["triage_class"],"SHARED_KEYWORDS_CANDIDATE")

    def test_broad_reuse_requires_bidirectional_coverage(self):
        e=sample("W badaniu oceniono przyrost skuteczności modelu detekcji",
                 "Oceniono przyrost skuteczności modelu detekcji w badaniu")
        broad=classify(make_pair(.61,.79,[e,e]))
        narrow=classify(make_pair(.61,.02,[e,e]))
        self.assertEqual(broad["triage_class"],
                         "BROAD_CONTENT_REUSE_CANDIDATE")
        self.assertEqual(narrow["triage_class"],
                         "TOPIC_SIMILARITY_LOW_COVERAGE")
        self.assertGreater(broad["harmonic_coverage"],narrow["harmonic_coverage"])

    def test_summary_order_preserves_source_and_is_read_only(self):
        source={
            "schema_version":"0.1.0",
            "source_revision":"c"*40,
            "candidate_pairs_total":68,
            "verified":False,
            "pairs":[
                make_pair(.02,.03,[sample("Słowa kluczowe: X","Keywords: X")],
                          score=.99),
                make_pair(.61,.79,[sample("tekst analizy","tekst analizy")]*2,
                          score=.95),
            ]
        }
        result=summarize(source)
        self.assertEqual(result["pairs"][0]["triage_class"],
                         "BROAD_CONTENT_REUSE_CANDIDATE")
        self.assertEqual(result["pairs_retained"],2)
        self.assertEqual(result["candidate_pairs_total"],68)
        self.assertFalse(result["verified"])
        with TemporaryDirectory() as name:
            root=Path(name)
            save(result,root/"report")
            self.assertEqual(json.loads((root/"report/semantic_triage.json").read_text(
                encoding="utf-8"))["pairs_retained"],2)
            self.assertTrue((root/"report/semantic_triage.md").exists())

    def test_reject_unverified_schema_assumptions(self):
        with self.assertRaises(ValueError):
            summarize({"schema_version":"bad"})
        with self.assertRaises(ValueError):
            summarize({"schema_version":"0.1.0","verified":True})


if __name__=="__main__":
    unittest.main()
