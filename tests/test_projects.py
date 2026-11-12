"""Minimalne testy integralności danych projektów wyświetlanych na stronie."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/projects.json"
TRANSLATIONS = ROOT / "docs/data/projects.en.json"
HTML = ROOT / "index.html"
DETAILS = ROOT / "docs/data/project-details.json"
PREVIEW_JS = ROOT / "docs/assets/js/project-preview.js"
PREVIEW_CSS = ROOT / "docs/assets/css/project-preview.css"


class ProjectsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = json.loads(DATA.read_text(encoding="utf-8"))
        cls.translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))

    def test_project_data_is_valid(self):
        """Sprawdzaj strukturę danych, nie liczbę, nazwy ani treść opisów."""
        self.assertIsInstance(self.projects, list)
        self.assertTrue(self.projects)

        titles = []
        for project in self.projects:
            with self.subTest(project=project.get("title")):
                self.assertIsInstance(project, dict)
                self.assertIn(project.get("phase"), {"current", "previous"})
                for key in ("title", "period", "description"):
                    self.assertIsInstance(project.get(key), str)
                    self.assertTrue(project[key].strip())
                titles.append(project["title"])

        self.assertEqual(len(titles), len(set(titles)))

    def test_english_translations_cover_all_projects(self):
        """Każdy projekt ma odpowiadający rekord EN, bez kontroli sformułowań."""
        self.assertIsInstance(self.translations, list)
        self.assertEqual(len(self.projects), len(self.translations))

        for project, translation in zip(self.projects, self.translations):
            with self.subTest(project=project["title"]):
                self.assertIsInstance(translation, dict)
                self.assertEqual(translation.get("sourceTitle"), project["title"])
                for key in ("title", "period", "description"):
                    self.assertIsInstance(translation.get(key), str)
                    self.assertTrue(translation[key].strip())

    def test_preview_metadata_covers_projects_and_languages(self):
        metadata = json.loads(DETAILS.read_text(encoding="utf-8"))
        self.assertEqual(set(metadata), {item["title"] for item in self.projects})
        for name, entry in metadata.items():
            with self.subTest(name=name):
                for language in ("pl", "en"):
                    self.assertIn(language, entry)
                    self.assertTrue(entry[language]["methods"])
                    self.assertTrue(all(isinstance(x, str) and x.strip() for x in entry[language]["methods"]))

    def test_logos_and_optional_project_links(self):
        """Każdy wpis logo jest bezpieczną, istniejącą grafiką lokalną."""
        metadata = json.loads(DETAILS.read_text(encoding="utf-8"))
        logo_pattern = re.compile(r"docs/assets/images/projects/[a-z0-9][a-z0-9_-]*[.](svg|png|webp)$")
        for name, entry in metadata.items():
            with self.subTest(project=name):
                logo = entry.get("logo")
                if logo is not None:
                    self.assertIsInstance(logo, str)
                    self.assertRegex(logo, logo_pattern)
                    target = ROOT / logo
                    self.assertTrue(target.is_file(), logo)
                    if target.suffix == ".svg":
                        self.assertIn("<svg", target.read_text(encoding="utf-8"))
                    elif target.suffix == ".png":
                        self.assertEqual(target.read_bytes()[:8], bytes.fromhex("89504e470d0a1a0a"))
                    elif target.suffix == ".webp":
                        data = target.read_bytes()[:12]
                        self.assertEqual(data[:4], b"RIFF")
                        self.assertEqual(data[8:12], b"WEBP")
                links = entry.get("links", [])
                self.assertIsInstance(links, list)
                for link in links:
                    self.assertIsInstance(link, dict)
                    self.assertIsInstance(link.get("label"), str)
                    self.assertTrue(link["label"].strip())
                    url = link.get("url")
                    self.assertIsInstance(url, str)
                    self.assertTrue(url.startswith("https://") and " " not in url and "@" not in url.split("/", 3)[2])

    def test_project_preview_is_wired(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertIn("project-preview.js", html)
        self.assertIn("project-preview.css", html)
        self.assertIn("ProjectPreview.attach", html)
        self.assertIn("project-details.json", html)
        js = PREVIEW_JS.read_text(encoding="utf-8")
        self.assertIn("showModal()", js)
        self.assertIn("projectLogoPath", js)
        self.assertIn("safeProjectLink", js)
        self.assertIn("project-logo", PREVIEW_CSS.read_text(encoding="utf-8"))
        self.assertIn("pointerenter", js)
        self.assertIn("focusin", js)
        self.assertIn("Escape", js)
        self.assertIn("setTimeout(()=>show(card,project,language),250)", js)

    def test_page_contains_project_data_hook(self):
        """Strona ma kontener projektów i odwołanie do danych."""
        html = HTML.read_text(encoding="utf-8")
        self.assertIn('id="projects-list"', html)
        self.assertIn("docs/data/projects.json", html)


if __name__ == "__main__":
    unittest.main()
