"""Spójność aktualnego katalogu materiałów studenckich."""
from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "materials"
SUBJECTS = (
    "bash", "latex", "git", "vim", "algorytmy", "aplikacje-mobilne",
    "psychoinformatyka", "robotyka-afektywna", "informatyka-poznawcza",
    "seminaria-dyplomowe",
)


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs).get("href"))


class MaterialsTests(unittest.TestCase):
    def test_index_links_resolve(self):
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script", html)
        self.assertIn("font:14px/1.5", html)
        self.assertIn("a:focus-visible", html)
        self.assertNotIn("library/", html)
        parser = Anchors()
        parser.feed(html)
        self.assertTrue(parser.links)
        for href in parser.links:
            with self.subTest(href=href):
                self.assertTrue(href)
                self.assertFalse(urlsplit(href).scheme)
                path = unquote(urlsplit(href).path)
                target = (MATERIALS / path).resolve()
                self.assertTrue(target.is_relative_to(ROOT))
                if target.is_dir():
                    target /= "index.html"
                self.assertTrue(target.is_file(), href)

    def test_expected_html_pages_exist(self):
        for subject in SUBJECTS:
            self.assertTrue((MATERIALS / subject / "index.html").is_file())
        for number in range(2, 7):
            self.assertTrue((MATERIALS / f"ndp_lab_{number:02}.html").is_file())
        for number in range(1, 5):
            self.assertTrue((MATERIALS / f"wirr_blok_{number:02}.html").is_file())

    def test_legacy_scaffolding_absent(self):
        for path in ("wirr", "lectures", "library", "f", "h", "p",
                     "materials/wirr", "assets/wirr.js",
                     "assets/library.json", "tools/build_library.py"):
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists())


if __name__ == "__main__":
    unittest.main()
