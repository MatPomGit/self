"""Tests for stable, short PDF viewer links on GitHub Pages."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.build_short_links import build, pdf_routes, rewrite_index, viewer_html

ROOT = Path(__file__).resolve().parents[1]


class ShortLinkTests(unittest.TestCase):
    def test_real_course_examples(self):
        routes = pdf_routes(ROOT / "files")
        self.assertEqual(routes["narzędzia-dla-programistów/ndp__lab__04.pdf"], "ndp/lab04/")
        self.assertEqual(routes["wirtualna-i-rozszerzona-rzeczywistosc/wirr_w07.pdf"], "wirr/w07/")
        self.assertEqual(len(routes), len(set(routes.values())))
        self.assertGreater(len(routes), 100)

    def test_rendered_site_keeps_pdf_bytes_and_displays_short_links(self):
        with TemporaryDirectory() as temp:
            site = Path(temp)
            files = site / "files"
            ndp = files / "narzędzia-dla-programistów"
            wirr = files / "wirtualna-i-rozszerzona-rzeczywistosc"
            ndp.mkdir(parents=True)
            wirr.mkdir(parents=True)
            (ndp / "ndp__lab__04.pdf").write_bytes(b"%PDF-mock-ndp")
            (wirr / "wirr_w07.pdf").write_bytes(b"%PDF-mock-wirr")
            (wirr / "wirr_lab_04.pdf").write_bytes(b"%PDF-mock-lab")
            (wirr / "Lab_4_XR.pdf").write_bytes(b"%PDF-mock-legacy")

            original_index = (
                '<a href="narzędzia-dla-programistów/ndp__lab__04.pdf" download title="NDP">NDP</a>\n'
                '<a href="wirtualna-i-rozszerzona-rzeczywistosc/wirr_w07.pdf" download>WiRR</a>\n'
                '<a href="wirtualna-i-rozszerzona-rzeczywistosc/wirr_lab_04.pdf">Lab</a>\n'
                '<a href="https://example.org/more.pdf">External</a>\n'
            )
            (files / "index.html").write_text(original_index, encoding="utf-8")
            aliases = pdf_routes(files)
            self.assertEqual(aliases["wirtualna-i-rozszerzona-rzeczywistosc/wirr_lab_04.pdf"], "wirr/lab04/")
            self.assertEqual(aliases["wirtualna-i-rozszerzona-rzeczywistosc/Lab_4_XR.pdf"], "wirr/lab04-xr/")

            self.assertEqual(build(site, check=True), (4, 3))
            self.assertFalse((files / "ndp" / "lab04").exists())
            self.assertEqual((files / "index.html").read_text(encoding="utf-8"), original_index)

            self.assertEqual(build(site), (4, 3))
            index = (files / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="ndp/lab04/"', index)
            self.assertIn('href="wirr/w07/"', index)
            self.assertIn('data-original-url="narzędzia-dla-programistów/ndp__lab__04.pdf"', index)
            self.assertIn('href="https://example.org/more.pdf"', index)
            self.assertNotIn('href="ndp/lab04/" download', index)

            page = (files / "ndp" / "lab04" / "index.html").read_text(encoding="utf-8")
            self.assertIn('<iframe src="/files/narz%C4%99dzia-dla-programist%C3%B3w/ndp__lab__04.pdf"', page)
            self.assertIn('href="/files/narz%C4%99dzia-dla-programist%C3%B3w/ndp__lab__04.pdf" download', page)
            self.assertEqual((ndp / "ndp__lab__04.pdf").read_bytes(), b"%PDF-mock-ndp")

    def test_no_stale_or_duplicate_aliases(self):
        with TemporaryDirectory() as temp:
            files = Path(temp) / "files"
            folder = files / "psychoinformatyka"
            folder.mkdir(parents=True)
            (folder / "pi_w01.pdf").write_bytes(b"x")
            (files / "index.html").write_text('<a href="psychoinformatyka/pi_w01.pdf">PDF</a>', encoding="utf-8")
            (files / "pi" / "w01").mkdir(parents=True)
            (files / "pi" / "w01" / "index.html").write_text("Existing", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "overwrite"):
                pdf_routes(files)

    def test_papers_markdown_moved_without_loss(self):
        self.assertFalse((ROOT / "docs" / "papers.md").exists())
        moved = ROOT / "docs" / "data" / "papers.md"
        self.assertTrue(moved.is_file())
        self.assertIn("# Publikacje naukowe", moved.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
