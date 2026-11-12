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
      "## Bibliografia i dokumentacja techniczna"))
]
class ConsolidatedReportTests(unittest.TestCase):
    def test_required_sections_and_source_provenance(self):
        for path,sections in DOCS:
            with self.subTest(path=path):
                text=(ROOT/path).read_text(encoding="utf-8")
                self.assertGreater(len(text),10000)
                self.assertIn("wersja 1.0.0",text)
                self.assertIn("## Pochodzenie i zakres weryfikacji",text)
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

if __name__=="__main__":
    unittest.main()
