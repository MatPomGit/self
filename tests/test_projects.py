"""Spójność promocyjnej karty projektów, dat i wersji językowych."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/projects.json"
TRANSLATIONS = ROOT / "docs/data/projects.en.json"
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

CURRENT = [
    "ARC-RGBT",
    "ARC-RVI · Autonomiczna inspekcja wizualna",
    "ARC-HRI-SAFETY",
    "ARC-AFFECTIVE",
    "ContextNDD",
    "SAPIENS · Człowiek i robot humanoidalny",
    "ARC Mobile Eye Tracking",
    "EEG Neurolyze",
    "S4D-TAM · Nawigacja autonomiczna",
    "ARC Attachment Dynamics",
    "ARC-ADHD · Adaptacyjna gra badawcza",
    "AI Cognitive Resilience",
    "DERA-HRI · Emocje w interakcji z robotem",
    "MindDx · Symulator diagnozy psychologicznej",
]
PREVIOUS = [
    "ARIANA",
    "PIAST · Satelitarne obrazowanie Ziemi",
    "SEEKER · Głowice optoelektroniczne",
    "PolFEL · Laser na swobodnych elektronach",
    "OPTOKRYPT · Kryptografia kwantowa",
    "Eye Tracking w rzeczywistości mieszanej",
    "Systemy wizyjne XR w nauce i obronności",
    "RiverGUARD · Ochrona granic rzecznych",
    "Skaner 3D sub-THz",
    "Sensor trenażera GROM / PIORUN",
    "PROTECT · Biometria kontroli granicznej",
]


class ProjectsTests(unittest.TestCase):
    def test_current_and_previous_portfolio(self):
        projects = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual([p["title"] for p in projects if p["phase"] == "current"], CURRENT)
        self.assertEqual([p["title"] for p in projects if p["phase"] == "previous"], PREVIOUS)
        self.assertEqual(len(projects), 25)
        self.assertEqual(len({p["title"] for p in projects}), len(projects))

    def test_dates_copy_and_no_outbound_links(self):
        projects = json.loads(DATA.read_text(encoding="utf-8"))
        for project in projects:
            with self.subTest(project=project["title"]):
                self.assertIn(project["phase"], ("current", "previous"))
                self.assertTrue(project["period"].strip())
                self.assertTrue(project["description"].strip())
                self.assertLessEqual(len(project["description"]), 270)
                self.assertNotIn("http://", str(project))
                self.assertNotIn("https://", str(project))
                self.assertNotIn("github.com", str(project))
                self.assertNotIn("doi.org", str(project))
                if project["period"] != "Data do potwierdzenia":
                    self.assertRegex(project["period"], r"^20\d{2}(?:[–-]20\d{2}|[–-]obecnie)?$")
        uncertain = [p["title"] for p in projects if p["period"] == "Data do potwierdzenia"]
        self.assertEqual(uncertain, ["Sensor trenażera GROM / PIORUN"])

    def test_bilingual_project_data(self):
        projects = json.loads(DATA.read_text(encoding="utf-8"))
        translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
        self.assertEqual(len(projects), len(translations))
        self.assertEqual([p["title"] for p in projects], [p["sourceTitle"] for p in translations])
        for project in translations:
            with self.subTest(project=project["sourceTitle"]):
                self.assertTrue(project["title"].strip())
                self.assertTrue(project["period"].strip())
                self.assertTrue(project["description"].strip())
        self.assertEqual(sum(p["period"] == "2026–present" for p in translations), len(CURRENT))

    def test_promotional_ui_has_sections_and_no_project_links(self):
        panel = re.search(r'<article class="panel" id="projekty"[^>]*>[\s\S]*?</article>', HTML)
        self.assertIsNotNone(panel)
        self.assertNotIn("<a ", panel.group(0))
        self.assertIn('id="projects-list"', panel.group(0))
        self.assertIn("Aktualne programy badawczo-rozwojowe", HTML)
        self.assertIn("Wybrane projekty i konsorcja", HTML)
        self.assertIn("makeElement('div','project-period',entry.period)", HTML)
        self.assertIn("loadData('docs/data/projects.json'", HTML)
        renderer = HTML.split("function renderProjects(records){", 1)[1].split("let publicationRecords", 1)[0]
        self.assertNotIn("createElement('a'", renderer)
        self.assertNotIn("makeElement('a'", renderer)
        self.assertNotIn("href", renderer)

    def test_cards_have_consistent_height_and_hover(self):
        # Each grid uses equal-size implicit rows. The tallest card determines
        # the row height without clipping translations or long descriptions.
        self.assertIn(".project-cards{margin-top:12px;grid-auto-rows:1fr}", HTML)
        self.assertIn("display:flex;flex-direction:column;min-height:220px;height:100%", HTML)
        self.assertIn("background:var(--accent-soft)", HTML)
        self.assertIn(".project-cards .data-card:hover", HTML)
        self.assertIn('data-theme="dark"] .project-cards .data-card:hover', HTML)
        self.assertIn("background:var(--raised)", HTML)
        self.assertIn("box-shadow:0 4px 16px", HTML)
        self.assertIn("@media(hover:hover)", HTML)
        self.assertIn(".project-cards .data-card{transition:none}", HTML)
        self.assertNotIn("overflow:hidden", HTML.split(".project-cards{", 1)[1].split(".data-card .project-period", 1)[0])
        self.assertNotIn("cursor:pointer", HTML.split(".project-cards{", 1)[1].split(".data-card .project-period", 1)[0])

    def test_version(self):
        self.assertIn("v1.2.17", HTML)


if __name__ == "__main__":
    unittest.main()
