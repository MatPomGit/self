"""Deterministic tests for the pilot lexical overlap audit (#138)."""
import json
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
from xml.sax.saxutils import escape
from xml.sax.saxutils import escape

from scripts.audit_content_overlap import (compute, doc_key, grams, write_reports,
    audit_manifest, pair_matrix_csv, ExtractionCache)


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
            rendered_summary = (output / 'summary.md').read_text(encoding='utf-8')
            self.assertIn('UNVERIFIED', rendered_summary)
            self.assertIn(f"Source SHA: `{result['source_revision']}`", rendered_summary)
            self.assertNotIn("\\`", rendered_summary)
            saved = json.loads((output / 'overlap.json').read_text(encoding='utf-8'))
            self.assertEqual(saved['counts'], result['counts'])
            self.assertEqual((scope / 'Pierwsza.docx').read_bytes(), prior)

    def test_manifest_and_matrix_are_reproducible_and_traceable(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            scope = root / "files/inne/analizy"
            sample = ("Wspólne metody przetwarzania sygnałów multimodalnych "
                      "oraz analiza porównawcza wyników badania. ") * 14
            sample_docx(scope / "A.docx", sample + "Dodatkowe szczegóły.")
            sample_docx(scope / "B.docx", sample + "Unikalna interpretacja.")
            report = compute(root, scope)
            first = audit_manifest(report)
            second = audit_manifest(compute(root, scope))
            self.assertEqual(first, second)
            self.assertEqual(len(first["sources"]), 2)
            self.assertEqual(first["parameters"]["ngram"], 5)
            self.assertEqual(first["pair_decisions"], "UNVERIFIED: candidate discovery only")
            self.assertTrue(all(len(x["sha256"]) == 64 for x in first["sources"]))
            self.assertEqual(pair_matrix_csv(report), pair_matrix_csv(compute(root, scope)))
            target = root / "reports"
            write_reports(report, target, top=3)
            manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest, first)
            with (target / "matrix.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), len(report["pairs"]))
            self.assertTrue(rows)
            for row in rows:
                self.assertEqual(row["verified"], "false")
                self.assertTrue(isinstance(json.loads(row["evidence_json"]), list))
                self.assertEqual(set(row), set(pair_matrix_csv(report).splitlines()[0].split(",")))
            self.assertFalse((scope / "manifest.json").exists())

    def test_csv_has_header_when_no_pairs_exist(self):
        result = {"pairs": []}
        data = pair_matrix_csv(result)
        self.assertEqual(len(data.splitlines()), 1)
        self.assertIn("evidence_json", data)

    def test_cache_incremental_equivalence_invalidation_and_repair(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            scope = root / "files/inne/analizy"
            cache_dir = root / "reports/extraction-cache"
            sample = ("Analiza rozpoznawania sygnałów multimodalnych "
                      "opiera się na takich samych danych wejściowych. ") * 12
            sample_docx(scope / "A.docx", sample + "Pierwsza konkluzja.")
            sample_docx(scope / "B.docx", sample + "Druga konkluzja.")
            before = {p.name: p.read_bytes() for p in scope.iterdir()}

            initial_cache = ExtractionCache(root, cache_dir)
            initial = compute(root, scope, cache=initial_cache)
            self.assertEqual(initial_cache.stats(),
                             {"hits": 0, "misses": 2, "invalid": 0, "writes": 2})
            self.assertEqual({p.name: p.read_bytes() for p in scope.iterdir()}, before)

            warm_cache = ExtractionCache(root, cache_dir)
            warm = compute(root, scope, cache=warm_cache)
            self.assertEqual(warm_cache.stats(),
                             {"hits": 2, "misses": 0, "invalid": 0, "writes": 0})
            self.assertEqual(audit_manifest(initial), audit_manifest(warm))
            self.assertEqual(pair_matrix_csv(initial), pair_matrix_csv(warm))
            self.assertEqual(initial["formats"], warm["formats"])
            self.assertEqual(initial["pairs"], warm["pairs"])

            sample_docx(scope / "A.docx", sample + "Zmodyfikowany wynik.")
            incremental_cache = ExtractionCache(root, cache_dir)
            changed = compute(root, scope, cache=incremental_cache)
            self.assertEqual(incremental_cache.stats(),
                             {"hits": 1, "misses": 1, "invalid": 0, "writes": 1})
            full = compute(root, scope)
            self.assertEqual(audit_manifest(changed), audit_manifest(full))
            self.assertEqual(pair_matrix_csv(changed), pair_matrix_csv(full))

            # A malformed cache file must be ignored and the original re-read.
            target = incremental_cache._entry("files/inne/analizy/B.docx",
                                              full["files"][1]["sha256"])
            target.write_text("{corrupted JSON", encoding="utf-8")
            repair_cache = ExtractionCache(root, cache_dir)
            repaired = compute(root, scope, cache=repair_cache)
            self.assertEqual(repair_cache.stats(),
                             {"hits": 1, "misses": 1, "invalid": 1, "writes": 1})
            self.assertEqual(audit_manifest(repaired), audit_manifest(full))

    def test_cache_cannot_be_placed_in_published_materials(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for public_dir in ("files/cache", "docs/cache",
                               "_site/cache"):
                with self.subTest(public_dir=public_dir):
                    with self.assertRaises(ValueError):
                        ExtractionCache(root, root / public_dir)
            cache = ExtractionCache(root, root / "reports/cache")
            self.assertTrue(cache.directory.is_dir())

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
