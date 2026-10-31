"""Spójność indeksu materiałów z opublikowanymi plikami."""
from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "materials"
SUBJECTS = (
    "psychoinformatyka",
    "robotyka-afektywna",
    "informatyka-poznawcza",
)


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs).get("href"))


class MaterialsTests(unittest.TestCase):
    def test_index_links_and_inventory(self):
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count("<script>"), 2)
        self.assertNotIn("<script src=", html)
        self.assertIn("self-theme", html)
        self.assertIn('id="theme-toggle"', html)
        self.assertIn("color-scheme:dark", html)
        self.assertIn("font:14px/1.5", html)
        self.assertIn("a:focus-visible", html)
        self.assertIn('class="materials-grid"', html)
        self.assertGreaterEqual(html.count('class="materials-group"'), 10)
        self.assertIn("wirr_lab_08.pdf", html)
        self.assertIn("ndp__lab__10.pdf", html)
        self.assertIn("ra_w7.pdf", html)
        self.assertNotIn('href="library/', html)

        parser = Anchors()
        parser.feed(html)
        self.assertTrue(parser.links)
        linked_files = set()
        for href in parser.links:
            with self.subTest(href=href):
                self.assertTrue(href)
                self.assertFalse(urlsplit(href).scheme)
                target = (MATERIALS / unquote(urlsplit(href).path)).resolve()
                self.assertTrue(target.is_relative_to(ROOT))
                if target.is_dir():
                    target /= "index.html"
                self.assertTrue(target.is_file(), href)
                linked_files.add(target)

        public_files = {
            path.resolve() for path in MATERIALS.rglob("*")
            if path.is_file() and path != MATERIALS / "index.html"
        }
        self.assertFalse(
            public_files - linked_files,
            f"Pliki pominięte w indeksie: {sorted(public_files - linked_files)}",
        )

    def test_expected_html_pages_exist(self):
        for subject in SUBJECTS:
            self.assertTrue((MATERIALS / subject / "index.html").is_file())
        ndp = MATERIALS / "narzędzia-dla-programistów"
        wirr = MATERIALS / "wirtualna-i-rozszerzona-rzeczywistosc"
        for number in range(2, 7):
            self.assertTrue((ndp / f"ndp_lab_{number:02}.html").is_file())
        for number in range(1, 5):
            self.assertTrue((wirr / f"wirr_blok_{number:02}.html").is_file())

    def test_removed_subject_pages_absent(self):
        for subject in ("bash", "latex", "git", "vim",
                        "algorytmy", "aplikacje-mobilne"):
            with self.subTest(subject=subject):
                self.assertFalse((MATERIALS / subject / "index.html").exists())
        for name in ("ascii_player", "student", "system_tui"):
            self.assertTrue(
                (MATERIALS / "narzędzia-dla-programistów" / name).is_file()
            )

    def test_legacy_scaffolding_absent(self):
        for path in ("wirr", "lectures", "library", "f", "h", "p",
                     "materials/wirr", "assets/wirr.js",
                     "assets/library.json", "tools/build_library.py"):
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists())


if __name__ == "__main__":
    unittest.main()
