"""Editorial guards for canonical consolidated reports (#138)."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=[
    ("docs/consolidated/analiza_afektywna.md",
     ("## Streszczenie","## 2. Modele reprezentowania afektu",
      "## 5. Wdrożenie w architekturze Edge","## 7. Ograniczenia psychometryczne",
      "## Bibliografia")),
    ("docs/consolidated/isaac_lab.md",
     ("## Streszczenie","## 2. Uczenie polityk i projekt AGILE",
      "## 3. Isaac Lab-Arena","## 5. Real-to-sim",
      "## Bibliografia i dokumentacja techniczna")),
    ("docs/consolidated/telediagnostyka_ndd.md",
     ("## Streszczenie", "## 3. Trzy różne badania i ich wyniki",
      "## 4. Metryki klasyfikacji", "## 7. Zestawienie i pochodzenie treści",
      "## Bibliografia"))
]
class ConsolidatedReportTests(unittest.TestCase):
    def test_required_sections_and_source_provenance(self):
        for path,sections in DOCS:
            with self.subTest(path=path):
                text=(ROOT/path).read_text(encoding="utf-8")
                self.assertGreater(len(text),10000)
                self.assertRegex(text, r"wersja 1\.\d+\.\d+")
                self.assertTrue("## Pochodzenie i zakres weryfikacji" in text or
                                "## 7. Zestawienie i pochodzenie treści" in text)
                for section in sections:
                    self.assertIn(section,text)
                self.assertNotIn("TODO",text)
                self.assertNotIn("PDF-001",text)
                self.assertNotIn("## Aneks kontrolny",text)
                self.assertGreaterEqual(text.count("|---|"),0)
    def test_affective_both_tables_and_no_clinical_diagnostic_shortcut(self):
        text=(ROOT/DOCS[0][0]).read_text(encoding="utf-8")
        self.assertIn("| Krótkie |",text)
        self.assertIn("| Edge |",text)
        self.assertIn("nie bezpośrednie i jednoznaczne czujniki emocji",text)
        self.assertIn("2024/1689",text)
    def test_isaac_physical_system_distinctions(self):
        text=(ROOT/DOCS[1][0]).read_text(encoding="utf-8")
        for term in ("Isaac Sim","Isaac Lab-Arena","WBC-AGILE",
                     "OpenUSD","Cosmos","sim-to-real"):
            self.assertIn(term,text)
        self.assertIn("nie silnikiem fizycznym",text)
        self.assertIn("Core API i migracja",text)
        self.assertIn("isaacsim.core.experimental",text)
    def test_ndd_distinguishes_independent_studies_and_metrics(self):
        text=(ROOT/DOCS[2][0]).read_text(encoding="utf-8")
        for term in ("1688", "342", "704", "99,71%", "84%", "86%", "68%", "69%",
                     "Swoistość i precyzja nie są synonimami",
                     "TRIPOD+AI", "PROBAST+AI"):
            self.assertIn(term, text)

if __name__=="__main__":
    unittest.main()
