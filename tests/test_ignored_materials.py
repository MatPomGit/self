"""Permanent guard: files/ignored is never indexed or published.

This test is intentionally independent of the materials index generator.
"""
from pathlib import Path
import unittest

from scripts.sync_materials import inventory
from scripts.build_short_links import pdf_routes

ROOT = Path(__file__).resolve().parents[1]
FILES = ROOT / "files"
OLD = [
    "Isaac Lab i bliźniaki cyfrowe.pdf",
    "Isaac_Lab.docx",
    "Isaac_Lab.pdf",
    "Synteza Modeli multimodalnych.docx",
    "Zautomatyzowana_analiza_afektywna.pdf",
]
NEW = [
    "analiza_afektywna.docx", "analiza_afektywna.pdf",
    "isaac_lab.docx", "isaac_lab.pdf",
]


class IgnoredArchivePolicyTests(unittest.TestCase):
    def test_old_sources_exist_only_in_archive(self):
        for filename in OLD:
            with self.subTest(filename=filename):
                self.assertTrue((FILES / "ignored/inne/analizy" / filename).is_file())
                self.assertFalse((FILES / "inne/analizy" / filename).exists())

    def test_new_public_downloads_are_valid(self):
        from pypdf import PdfReader
        from zipfile import ZipFile
        for filename in NEW:
            path = FILES / "inne/analizy" / filename
            with self.subTest(filename=filename):
                self.assertTrue(path.is_file())
                if filename.endswith(".pdf"):
                    reader = PdfReader(str(path))
                    self.assertGreaterEqual(len(reader.pages), 2)
                    self.assertIn("Bibliografia", " ".join(p.extract_text() or "" for p in reader.pages))
                else:
                    with ZipFile(path) as archive:
                        self.assertIn("word/document.xml", archive.namelist())

    def test_inventory_and_aliases_exclude_archive(self):
        names = inventory(FILES)
        self.assertFalse(any(path.startswith("ignored/") for path in names))
        self.assertTrue(all("inne/analizy/" + n in names for n in NEW))
        routes = pdf_routes(FILES)
        self.assertFalse(any(name.startswith("ignored/") for name in routes))
        self.assertIn("inne/analizy/isaac_lab.pdf", routes)
        self.assertIn("inne/analizy/analiza_afektywna.pdf", routes)

    def test_archive_is_not_linked_in_source_index(self):
        html = (FILES / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('href="ignored/', html)
        self.assertNotIn("data-materials-subject=\"ignored\"", html)

    def test_deployment_artifact_removes_archived_files(self):
        workflow = (ROOT / ".github/workflows/restore-original-pages.yml").read_text(
            encoding="utf-8")
        self.assertIn("rm -rf _site/files/ignored", workflow)
        self.assertLess(workflow.index("rm -rf _site/files/ignored"),
                        workflow.index("python scripts/build_short_links.py --site _site"))


if __name__ == "__main__":
    unittest.main()
