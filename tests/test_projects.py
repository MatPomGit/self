"""Regresja: zakładka Projekty odpowiada oficjalnemu wykazowi PRz."""
from __future__ import annotations

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/projects.json"
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SOURCE = "https://mpomianek.v.prz.edu.pl/praca-naukowa/uczestnictwo-w-organizacjach-i-projektach"

EXPECTED_TITLES = [
        "Projekt „ARIANA”",
        "Polish ImAging SaTellites „PIAST”",
        "Rodzina głowic optoelektronicznych dla rakiet sterowanych „SEEKER”",
        "„PolFEL” - Projekt polskiego lasera na swobodnych elektronach",
        "Kwantowy generator liczb losowych „OPTOKRYPT”",
        "Analysis of the possibility of using optoelectronic eye tracking systems as interaction interfaces in mixed reality systems",
        "Analysis of the possibilities of using mixed reality vision systems in scientific research and military applications (RMN/948/2018)",
        "Optoelektroniczny system do ochrony perymetrycznej granicy rzecznej „RiverGUARD”",
        "Active sub-THz 3D scanner for anti-terrorist applications (PBS3/B3/30/2015)",
        "Development of a sensor for a virtual trainer - anti-aircraft GROM and PIORUN missile sets",
        "Pervasive and User Focused Biometrics Border Project (Common and user-oriented biometric border design) EU–0700259 PROTECT"
]


class ProjectsTests(unittest.TestCase):
    def test_matches_official_list_order_and_count(self):
        projects = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual([p["title"] for p in projects], EXPECTED_TITLES)
        self.assertEqual(len(projects), 11)
        self.assertEqual(len(set(EXPECTED_TITLES)), 11)
        self.assertTrue(all(p["description"].strip() for p in projects))

    def test_no_previous_generic_project_cards(self):
        projects = json.loads(DATA.read_text(encoding="utf-8"))
        titles = [p["title"] for p in projects]
        for old in (
            "MEMS Eye-Tracking", "Varifocal HMD Calibration",
            "Digital Twin Validation", "VR Pipelines for Medical Data",
            "Kognitywna Robotyka Humanoidalna", "Technologie obronne",
            "Rehabilitacja XR", "Diagnostyka wspomagana AI",
        ):
            with self.subTest(old=old):
                self.assertNotIn(old, titles)

    def test_source_and_single_project_entry_point(self):
        self.assertIn('href="' + SOURCE + '"', HTML)
        self.assertIn('id="projects-list"', HTML)
        self.assertIn("loadData('docs/data/projects.json'", HTML)
        self.assertIn('>Wszystkie projekty</text>', HTML)
        self.assertNotIn('>OPTOKRYPT</text>', HTML)
        self.assertIn("if(entry.category)card.append(", HTML)

    def test_version(self):
        self.assertIn("v1.2.11", HTML)


if __name__ == "__main__":
    unittest.main()
