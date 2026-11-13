"""Regression tests for evidence-preserving consolidation drafts (#138).

Drafts are editorial starting points; tests do NOT certify scientific parity.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape
from zipfile import ZipFile
import unittest

from scripts.prepare_consolidation_drafts import (
    PAIRS, docx_blocks, markdown_table, pdf_review_windows, draft
)
from scripts.audit_content_overlap import Extracted, tokens

ROOT=Path(__file__).resolve().parents[1]


def docx_fixture(path):
    xml=(
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:r><w:t>Wprowadzenie do badania</w:t></w:r></w:p>'
        '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Metoda</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:t>Wynik</w:t></w:r></w:p></w:tc></w:tr>'
        '<w:tr><w:tc><w:p><w:r><w:t>Model A</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:t>80%</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
        '<w:p><w:r><w:t>Wnioski z badania</w:t></w:r></w:p></w:body></w:document>'
    )
    path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,"w") as z:
        z.writestr("word/document.xml",xml)


class ConsolidationDraftTests(unittest.TestCase):
    def test_docx_preserves_table_and_paragraph_order(self):
        with TemporaryDirectory() as temp:
            p=Path(temp)/"source.docx"
            docx_fixture(p)
            items=docx_blocks(p)
            self.assertEqual([x["type"] for x in items],
                             ["paragraph","table","paragraph"])
            self.assertEqual(items[1]["rows"][0],["Metoda","Wynik"])
            self.assertEqual(items[1]["rows"][1],["Model A","80%"])
            self.assertIn("Wprowadzenie",items[0]["text"])
            self.assertIn("Wnioski",items[-1]["text"])

    def test_pipe_characters_are_escaped_in_markdown_tables(self):
        rendered=markdown_table([["Col|1","Col2"],["a","b|c"]])
        self.assertIn(r"Col\|1",rendered)
        self.assertIn(r"b\|c",rendered)
        self.assertIn("| --- | --- |",rendered)

    def test_pdf_candidates_are_not_claimed_unique(self):
        a=" ".join(["W eksperymencie badano fuzję danych sensorycznych"]*28)
        b=" ".join(["Oddzielnie zastosowano analizę zachowania osób"]*24)
        doc=Extracted("pdf", "a"*64,"EXTRACTED",
                      [{"location":"str. 2","text":a+" "+b}],
                      tokens(a+" "+b))
        candidate=pdf_review_windows(doc,tokens(a))
        self.assertTrue(candidate)
        self.assertTrue(all(x["verified_unique"] is False for x in candidate))
        self.assertTrue(all("page" in x and "word_start" in x for x in candidate))

    def test_real_report_sources_preserved_and_draft_contains_content(self):
        scope=ROOT/"files/ignored/inne/analizy"
        self.assertEqual(len(PAIRS),2)
        for slug,title,base,other in PAIRS:
            with self.subTest(slug=slug):
                basefile=scope/base
                pdf=scope/other
                self.assertTrue(basefile.is_file())
                self.assertTrue(pdf.is_file())
                before=basefile.stat().st_size,pdf.stat().st_size
                md,ledger=draft(basefile,pdf,ROOT,slug=slug,title=title)
                self.assertIn("## Tekst bazowy z DOCX",md)
                self.assertIn("## Aneks kontrolny",md)
                self.assertIn(f"`{basefile.relative_to(ROOT).as_posix()}`", md)
                self.assertIn(f"`{pdf.relative_to(ROOT).as_posix()}`", md)
                self.assertNotIn(chr(92) + "`", md.split("## Tekst bazowy z DOCX")[0])
                self.assertIn("NIE jest jeszcze zweryfikowanym",md)
                self.assertTrue(len(md)>1500)
                self.assertEqual(len(ledger["sources"]),2)
                self.assertTrue(all(len(x["sha256"])==64 for x in ledger["sources"]))
                self.assertFalse(ledger["scientifically_verified"])
                self.assertFalse(ledger["completed_consolidation"])
                self.assertFalse(ledger["source_files_modified"])
                self.assertEqual((basefile.stat().st_size,pdf.stat().st_size),before)


if __name__=="__main__":
    unittest.main()
