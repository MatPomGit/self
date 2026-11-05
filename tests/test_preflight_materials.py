"""Document preflight must detect broken assets without touching valid materials."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from pypdf import PdfWriter

from scripts.preflight_materials import problem, quarantine, scan


class PreflightTests(unittest.TestCase):
    def test_valid_documents_and_invalid_stubs(self):
        with TemporaryDirectory() as tmp:
            materials = Path(tmp) / "materials"
            subject = materials / "course"
            subject.mkdir(parents=True)
            good_pdf = subject / "good.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=595, height=842)
            with good_pdf.open("wb") as output:
                writer.write(output)
            good_pptx = subject / "good.pptx"
            with ZipFile(good_pptx, "w") as archive:
                archive.writestr("ppt/presentation.xml", "<presentation/>")
            bad_pdf = subject / "empty.pdf"
            bad_pdf.write_bytes(b"\r\n")
            bad_pptx = subject / "empty.pptx"
            bad_pptx.write_bytes(b"\r\n")
            bad_docx = subject / "bad.docx"
            with ZipFile(bad_docx, "w") as archive:
                archive.writestr("word/other.xml", "<x/>")
            self.assertIsNone(problem(good_pdf))
            self.assertIsNone(problem(good_pptx))
            issues = scan(materials)
            self.assertEqual({relative.as_posix() for relative, _ in issues}, {
                "course/empty.pdf", "course/empty.pptx", "course/bad.docx"
            })
            destination = Path(tmp) / "quarantine"
            quarantine(materials, destination, issues)
            self.assertTrue(good_pdf.exists())
            self.assertTrue(good_pptx.exists())
            self.assertFalse(bad_pdf.exists())
            self.assertTrue((destination / "course/empty.pdf").exists())
            self.assertEqual(scan(materials), [])

    def test_reject_quarantine_inside_public_materials(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                quarantine(root, root / "quarantine", [])

    def test_truncated_pdf_header_and_trailer(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "damaged.pdf"
            path.write_bytes(b"not a PDF document, bytes")
            self.assertEqual(problem(path), "missing PDF header")
            path.write_bytes(b"%PDF-1.7\nmissing termination")
            self.assertEqual(problem(path), "missing PDF EOF marker")
            path.write_bytes(b"%PDF-1.4\n%%EOF\n")
            self.assertIn("unreadable PDF structure", problem(path))


if __name__ == "__main__":
    unittest.main()
