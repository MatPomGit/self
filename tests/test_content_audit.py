"""Deterministic tests for the pilot lexical overlap audit (#138)."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
from xml.sax.saxutils import escape

from scripts.audit_content_overlap import compute, doc_key, grams, write_reports


def sample_docx(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body><w:p><w:r><w:t>' + escape(content) +
           '</w:t></w:r></w:p></w:body></w:document>')
    with ZipFile(path, 'w') as package:
        package.writestr('word/document.xml', xml)


class ContentAuditTests(unittest.TestCase):
    def test_ngram_and_logical_document(self):
        self.assertIn(tuple('a b c d e'.split()), grams('a b c d e'.split()))
        self.assertEqual(doc_key('files/inne/analizy/Test.pdf'),
                         doc_key('files/inne/analizy/Test.docx'))

    def test_overlap_evidence_and_unmodified_sources(self):
        text = ('W tym eksperymencie zastosowano model multimodalny oraz identyczną '
                'procedurę kalibracji czujników i porównano miary skuteczności '
                'algorytmów na tym samym zbiorze obserwacji i metodzie analizy. ') * 4
        with TemporaryDirectory() as directory:
            root = Path(directory)
            scope = root / 'files/inne/analizy'
            sample_docx(scope / 'Pierwsza.docx', text + 'Własny wynik eksperymentalny.')
            sample_docx(scope / 'Druga.docx', text + 'Różny dodatkowy wynik.')
            sample_docx(scope / 'Trzecia.docx', 'Dane o przemysłowych sieciach robota.')
            # Malformed ODT with the same stem is an incomplete variant.
            (scope / 'Pierwsza.odt').write_bytes(b'invalid')
            prior = (scope / 'Pierwsza.docx').read_bytes()
            result = compute(root, scope)
            self.assertEqual(result['counts']['files'], 4)
            self.assertEqual(result['counts']['logical_documents'], 3)
            self.assertEqual(result['counts']['format_groups'], 1)
            self.assertEqual(result['counts']['extraction_incomplete'], 1)
            pair = next(x for x in result['pairs'] if
                        'pierwsza' in x['a'] + x['b'] and
                        'druga' in x['a'] + x['b'])
            self.assertGreater(pair['coverage_shorter_5gram'], .75)
            self.assertEqual(pair['classification'], 'NEAR_TEXT_DUPLICATE_CANDIDATE')
            self.assertTrue(pair['evidence'])
            self.assertFalse(pair['verified'])
            self.assertTrue(all(len(x['sha256']) == 64 for x in result['files']))
            output = root / 'report'
            write_reports(result, output, 8)
            self.assertIn('UNVERIFIED', (output / 'summary.md').read_text(encoding='utf-8'))
            saved = json.loads((output / 'overlap.json').read_text(encoding='utf-8'))
            self.assertEqual(saved['counts'], result['counts'])
            self.assertEqual((scope / 'Pierwsza.docx').read_bytes(), prior)

    def test_same_named_but_divergent_formats_are_independent(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            scope = root / "files/inne/analizy"
            left = ("System rozpoznaje gest dłoni i wyznacza punkty "
                    "śledzenia w obrazie z kamery. ")*12
            right = ("W laboratorium analizowano klimatyczne szeregi "
                     "i zmienność opadów na podstawie temperatury. ")*12
            sample_docx(scope / "Raport.docx", left)
            odt_xml = ('<office:document-content '
                       'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
                       'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
                       '<office:body><office:text><text:p>' +
                       escape(right) +
                       '</text:p></office:text></office:body></office:document-content>')
            with ZipFile(scope / "Raport.odt", "w") as archive:
                archive.writestr("content.xml", odt_xml)
            result = compute(root, scope)
            self.assertEqual(result["counts"]["logical_documents"], 2)
            self.assertEqual(result["counts"]["format_groups"], 1)
            self.assertEqual(result["counts"]["split_variants"], 1)
            self.assertEqual(result["formats"][0]["status"],
                             "FORMAT_VARIANTS_SPLIT_CANDIDATE")
            self.assertEqual(len({x["document_id"] for x in result["files"]}), 2)

    def test_audit_output_not_inside_published_directories(self):
        from scripts.audit_content_overlap import validate_output_dir
        with TemporaryDirectory() as name:
            root = Path(name)
            for folder in ("files", "docs", "materials", "_site"):
                with self.subTest(folder=folder):
                    with self.assertRaises(ValueError):
                        validate_output_dir(root, root / folder / "report")
            validate_output_dir(root, root / "reports/content-audit")

    def test_no_false_duplicate_for_unrelated_reports(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            scope = root / 'files/inne/analizy'
            sample_docx(scope / 'A.docx', 'Wyniki doświadczenia są niejednoznaczne.')
            sample_docx(scope / 'B.docx', 'Przeprowadzono testy odrębnych narzędzi.')
            result = compute(root, scope)
            self.assertEqual(result['counts']['pairs_flagged'], 0)
            self.assertEqual(result['counts']['extracted'], 2)


if __name__ == '__main__':
    unittest.main()
