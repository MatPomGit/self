"""Weryfikacja klasyfikacji PDF, PPTX i DOCX według wymiarów stron."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

from scripts.classify_materials import kind, dimensions, classify


class GeometryTests(unittest.TestCase):
    def test_dimensions(self):
        self.assertEqual(kind(1920, 1080), "lecture")
        self.assertEqual(kind(1024, 768), "lecture")
        self.assertEqual(kind(210, 297), "lab")
        self.assertEqual(kind(297, 210), "lab")
        self.assertEqual(kind(595.28, 841.89), "lab")
        self.assertIsNone(kind(1600, 1000))

    def test_pdfinfo(self):
        with patch("scripts.classify_materials.subprocess.run") as run:
            run.return_value = Mock(returncode=0, stdout="Page    1 size: 960 x 540 pts")
            self.assertEqual(dimensions(Path("sample.pdf")), (960., 540.))
            run.return_value = Mock(returncode=1, stdout="")
            self.assertIsNone(dimensions(Path("sample.pdf")))

    def test_office_files_and_link_overrides(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            slide = folder / "lab_slide.pptx"
            with ZipFile(slide, "w") as z:
                z.writestr("ppt/presentation.xml",
                    '<p:presentation xmlns:p="http://schemas.openxmlformats.org/'
                    'presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/>'
                    '</p:presentation>')
            doc = folder / "w01_notes.docx"
            with ZipFile(doc, "w") as z:
                z.writestr("word/document.xml",
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/'
                    'wordprocessingml/2006/main"><w:body><w:sectPr>'
                    '<w:pgSz w:w="11906" w:h="16838"/></w:sectPr>'
                    '</w:body></w:document>')
            self.assertEqual(kind(*dimensions(slide)), "lecture")
            self.assertEqual(kind(*dimensions(doc)), "lab")
            html = ('<li><a class="material-link--lab" href="lab_slide.pptx">X</a></li>'
                    '<li><a href="w01_notes.docx">Y</a></li>'
                    '<li><a href="missing.pdf">Z</a></li>')
            updated, changes = classify(html, folder)
            self.assertIn('class="material-link--lecture" href="lab_slide.pptx"', updated)
            self.assertIn('class="material-link--lab" href="w01_notes.docx"', updated)
            self.assertIn('<a href="missing.pdf">', updated)
            self.assertEqual(len(changes), 2)
            self.assertEqual(classify(updated, folder)[1], [])


if __name__ == "__main__":
    unittest.main()
