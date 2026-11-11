"""Regressions for evidence-oriented report passage comparisons (#138)."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from xml.sax.saxutils import escape
import unittest

from scripts.audit_content_overlap import Extracted
from scripts.audit_report_differences import PAIRS, MATCH_THRESHOLD, analyze, compare, passages, save

ROOT = Path(__file__).resolve().parents[1]


def doc(path, parts):
    return Extracted(path, "a"*64, "EXTRACTED",
                     [{"location":f"akapit {i+1}","text":p} for i,p in enumerate(parts)],
                     " ".join(parts).lower().split())


def write_docx(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body><w:p><w:r><w:t>' + escape(value) +
           '</w:t></w:r></w:p></w:body></w:document>')
    with ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)


class DifferenceTests(unittest.TestCase):
    def test_chunks_have_addresses(self):
        text = " ".join(f"wyraz{i}" for i in range(185))
        items = passages(doc("x", [text]), window=75, step=55)
        self.assertGreaterEqual(len(items), 3)
        self.assertEqual(items[0].ordinal, 1)
        self.assertEqual(items[1].ordinal, 56)
        self.assertEqual(items[0].location, "akapit 1")

    def test_exact_duplicate_has_alignment(self):
        body = ("W eksperymencie badano wielomodalny system percepcji i kalibracji "
                "oraz powtarzalność pomiarów na wspólnym zbiorze danych. ")*10
        result = compare(doc("A", [body]), doc("B", [body]), label="same")
        self.assertGreater(result["a_matched_fraction"], .95)
        self.assertTrue(result["aligned"])
        self.assertFalse(result["a_unmatched_candidates"])
        self.assertFalse(result["b_unmatched_candidates"])
        self.assertFalse(result["verified"])

    def test_partial_reuse_and_unmatched_candidates(self):
        shared = ("Eksperyment obejmował analizę neuronalnych danych pomiarowych "
                  "oraz rejestrowanie sygnałów w zadanym protokole badawczym. ")*10
        unique = ("Odrębna próba analizowała poznawcze aspekty adaptacji "
                  "i zmienność wyników w odmiennym kontekście. ")*12
        result = compare(doc("A", [shared, unique]), doc("B", [shared]), label="partial")
        self.assertTrue(result["aligned"])
        self.assertTrue(result["a_unmatched_candidates"])
        self.assertIn("akapit 2", result["a_unmatched_candidates"][0]["locator"])
        self.assertNotIn("MERGE", result["interpretation"])

    def test_divergent_format_variants(self):
        a = ("Gestem ręki użytkownik steruje przebiegiem prezentacji "
             "oraz interfejsem systemu i analizuje ruch. ")*13
        b = ("Klimat atmosferyczny i prognozowanie ciśnienia "
             "w modelach pogodowych wymaga danych. ")*13
        result = compare(doc("x.docx",[a]),doc("x.pdf",[b]),
                         label="format",same_stem=True)
        self.assertEqual(result["interpretation"],"FORMAT_VERSION_MISMATCH_CANDIDATE")

    def test_source_preservation_and_missing_inputs(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            scope=root/"files/inne/analizy"
            write_docx(scope/"A.docx","Zapis podstawowego badania z pomiarami.")
            write_docx(scope/"B.docx","Zapis drugiego badania z pomiarami.")
            original=(scope/"A.docx").read_bytes()
            result=analyze(root,scope,(("test","A.docx","B.docx"),
                                       ("missing","A.docx","C.pdf")))
            self.assertEqual(result["pairs"][1]["interpretation"],"MISSING_INPUT")
            save(result,root/"out")
            self.assertTrue((root/"out/comparison.json").exists())
            self.assertTrue((root/"out/comparison.md").exists())
            self.assertEqual((scope/"A.docx").read_bytes(),original)

    def test_pilot_sources_exist(self):
        scope=ROOT/"files/inne/analizy"
        self.assertEqual(len(PAIRS),4)
        for label,a,b in PAIRS:
            with self.subTest(label=label):
                self.assertTrue((scope/a).is_file())
                self.assertTrue((scope/b).is_file())
        self.assertGreater(MATCH_THRESHOLD,.5)


if __name__=="__main__":
    unittest.main()
