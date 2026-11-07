"""Minimalne testy integralności danych projektów wyświetlanych na stronie."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/projects.json"
TRANSLATIONS = ROOT / "docs/data/projects.en.json"
HTML = ROOT / "index.html"


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

    def test_page_contains_project_data_hook(self):
        """Strona ma kontener projektów i odwołanie do danych."""
        html = HTML.read_text(encoding="utf-8")
        self.assertIn('id="projects-list"', html)
        self.assertIn("docs/data/projects.json", html)


if __name__ == "__main__":
    unittest.main()
