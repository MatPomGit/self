"""Evidence extraction regressions for repeated claims (#138)."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
from xml.sax.saxutils import escape
from scripts.audit_content_overlap import Extracted, tokens
from scripts.audit_repeated_claims import (
    REPORTS, UNIQUE_PAIR, claim_candidates, distinct_passages,
    docx_tables, table_row_metrics, analyze, save
)

ROOT=Path(__file__).resolve().parents[1]


def fake_doc(path,sections):
    return Extracted(path,"a"*64,"EXTRACTED",
                     [{"location":f"akapit {i}", "text":s} for i,s
                      in enumerate(sections,1)],
                     tokens(" ".join(sections)))


def make_docx(path,paragraph,rows=None):
    ns="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    p=lambda val: "<w:p><w:r><w:t>"+escape(val)+"</w:t></w:r></w:p>"
    cells=lambda line: "".join("<w:tc>"+p(cell)+"</w:tc>" for cell in line)
    tbl=("<w:tbl>"+"".join("<w:tr>"+cells(r)+"</w:tr>" for r in (rows or []))+
         "</w:tbl>") if rows else ""
    xml=f'<w:document xmlns:w="{ns}"><w:body>{p(paragraph)}{tbl}</w:body></w:document>'
    path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,"w") as archive:
        archive.writestr("word/document.xml",xml)


class ClaimEvidenceTests(unittest.TestCase):
    def test_ear_claim_extracts_origin_without_semantic_verdict(self):
        source=fake_doc("a.docx",[
            "Zastosowano kamerę i detektor wizji maszynowej.",
            "EAR (Eye Aspect Ratio): lęk >20 mrugnięć/min oraz depresja "
            "przy EAR <0.2 przez ponad 0.5 s.",
        ])
        examples=claim_candidates(source,REPORTS["ear_diagnostic_inference"]["terms"])
        self.assertEqual(examples[0]["matching_patterns"],3)
        self.assertEqual(examples[0]["locator"],"akapit 2")
        self.assertIn("EAR",examples[0]["excerpt"])

    def test_random_forest_context_is_locator_addressable(self):
        source=fake_doc("a",[
            "W ustalonym podziale model las losowy dał 84% dla ADHD oraz "
            "86% dla ASD. Walidacja pięciokrotna wymaga osobnej oceny."
        ])
        found=claim_candidates(source,REPORTS["adhd_asd_rf_performance"]["terms"])
        self.assertEqual(found[0]["matching_patterns"],3)
        self.assertIn("86%",found[0]["excerpt"])

    def test_distinct_wording_does_not_claim_unique_knowledge(self):
        a=fake_doc("a",[("Badanie obejmowało wykrywanie postawy głowy "
                         "i geometrię mimiki na podstawie sygnału wideo. ")*14])
        b=fake_doc("b",[("Wyniki klasyfikacji danych oddechowych "
                         "poddano walidacji krzyżowej i analizie ryzyka. ")*14])
        candidates=distinct_passages(a,b)
        self.assertTrue(candidates)
        self.assertLess(candidates[0]["fraction_5gram_found_in_other"],.1)
        self.assertIs(candidates[0]["verified_unique"],False)

    def test_reordered_table_columns_are_not_mistaken_for_unique_data(self):
        from scripts.audit_content_overlap import grams, tokens
        # A PDF may flatten a table into another column order.
        pdf="Metoda Wartość Opis Robotyka 85 procent Analiza"
        docx="Opis Metoda Wartość Analiza Robotyka 85 procent"
        score=table_row_metrics(
            docx,grams(tokens(pdf)),set(tokens(pdf)))
        self.assertEqual(score["fraction_words_found_in_pdf"],1.)
        self.assertEqual(score["triage_flag"],"LAYOUT_REORDERING_POSSIBLE")

    def test_split_docx_header_is_restored_only_with_pdf_vocabulary(self):
        from scripts.audit_content_overlap import grams, tokens
        pdf="Lokalizacja przetwarzania Docelowe opóźnienie Przykładowe zastosowanie Przykład sprzętu"
        docx="Lokalizacja p rzetwarzania Docelowe o późnienie Przykładowe z astosowanie Przykład s przętu"
        score=table_row_metrics(docx,grams(tokens(pdf)),set(tokens(pdf)))
        self.assertEqual(score["fraction_words_found_in_pdf"],1.)
        self.assertEqual(score["fraction_5gram_found_in_pdf"],1.)
        # Generic single-letter Polish prepositions must not be recombined
        # when the hypothetical joined word is absent from the source.
        different=table_row_metrics("w laboratorium porównano pełne wyniki pomiaru podczas konferencji naukowej",
                                    grams(tokens(pdf)),set(tokens(pdf)))
        self.assertLess(different["fraction_words_found_in_pdf"],.4)

    def test_strongly_shared_sections_not_mislabelled_distinct(self):
        repeated=("Porównanie metod klasyfikacji emocji w systemach "
                  "multimodalnych na wielu próbach danych. ")*11
        a=fake_doc("a",[repeated])
        b=fake_doc("b",[repeated])
        self.assertFalse(distinct_passages(a,b))

    def test_docx_table_rows_keep_cells(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"example.docx"
            make_docx(path,"Wyniki eksperymentu.",[["Model","Wynik"],["SVM","87%"]])
            rows=docx_tables(path)
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[1]["cells"],["SVM","87%"])
            self.assertEqual(rows[1]["locator"],"tabela 1, wiersz 2")

    def test_real_reports_and_read_only_audit(self):
        scope=ROOT/"files/inne/analizy"
        for spec in REPORTS.values():
            for name in spec["files"]:
                with self.subTest(name=name):
                    self.assertTrue((scope/name).exists())
        for name in UNIQUE_PAIR:
            self.assertTrue((scope/name).exists())
        report=analyze(ROOT,scope)
        self.assertEqual(len(report["claims"]),2)
        for claim in report["claims"]:
            self.assertEqual(len(claim["documents"]),2)
            self.assertTrue(all(s["match_count"]>=1 for s in claim["documents"]))
            self.assertTrue(all(len(s["sha256"])==64 for s in claim["documents"]))
        self.assertFalse(report["source_files_modified"])
        with TemporaryDirectory() as tmp:
            save(report,Path(tmp))
            self.assertTrue((Path(tmp)/"claim_evidence.json").is_file())
            saved=json.loads((Path(tmp)/"claim_evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["schema_version"],"0.1.0")
            self.assertTrue((Path(tmp)/"claim_evidence.md").is_file())


if __name__=="__main__":
    unittest.main()
