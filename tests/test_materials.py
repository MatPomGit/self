"""Regression tests for the plain, canonical student materials directory."""
from __future__ import annotations

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "materials"

SUBJECTS = (
    "bash", "latex", "git", "vim", "algorytmy", "aplikacje-mobilne",
    "psychoinformatyka", "robotyka-afektywna", "informatyka-poznawcza",
    "seminaria-dyplomowe",
)
SCRIPTS = (
    "ascii_player", "bash-game.sh", "bash-rpg", "bash-vid.sh",
    "student", "system_tui",
)


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            self.links.append((attrs.get("href"), "download" in attrs))


class MaterialsTests(unittest.TestCase):
    def test_index_is_simple_and_all_links_exist(self):
        content = (MATERIALS / "index.html").read_text(encoding="utf-8")
        for forbidden in ("<script", "<style", "data-library=", "subject-card", 'href="#"'):
            self.assertNotIn(forbidden, content)

        parser = AnchorParser()
        parser.feed(content)
        self.assertTrue(parser.links)
        for href, downloadable in parser.links:
            with self.subTest(href=href):
                self.assertTrue(href)
                self.assertFalse(urlsplit(href).scheme)
                target = (MATERIALS / urlsplit(href).path).resolve()
                if target.is_dir():
                    target = target / "index.html"
                self.assertTrue(target.is_relative_to(ROOT))
                self.assertTrue(target.is_file(), href)
                if downloadable:
                    self.assertTrue(target.is_relative_to(MATERIALS))

    def test_manifest_students_sources_are_in_materials(self):
        data = json.loads((ROOT / "assets/library.json").read_text(encoding="utf-8"))
        for entry in data["entries"]:
            if entry["category"] not in ("Dydaktyka", "Bash", "WiRR", "Narzędzia"):
                continue
            with self.subTest(entry=entry["type"] + "/" + entry["id"]):
                source = entry["source"]
                self.assertTrue(source.startswith("materials/"), source)
                if entry.get("status") != "planned":
                    self.assertTrue((ROOT / source).is_file(), source)

    def test_subject_pages_and_scripts_are_under_materials(self):
        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                self.assertTrue((MATERIALS / subject / "index.html").is_file())
                old = (ROOT / (subject + ".html")).read_text(encoding="utf-8")
                self.assertIn('http-equiv="refresh"', old)
        for script in SCRIPTS:
            self.assertTrue((MATERIALS / "bash" / script).is_file())
            self.assertFalse((ROOT / "downloads" / "bash" / script).exists())

    def test_unpublished_pdfs_are_not_linked_as_files(self):
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        for n in range(1, 8):
            self.assertNotIn(f'href="wirr/w{n:02}.pdf"', html)


if __name__ == "__main__":
    unittest.main()
