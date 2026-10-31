"""Spójność indeksu materiałów z opublikowanymi plikami."""
from __future__ import annotations

import unittest
import re
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
        cards = re.findall(
            r'<section class="materials-group(?: materials-group--wide)?">'
            r'([\s\S]*?)</section>', html
        )
        self.assertEqual(len(cards), 10)
        for directory in (
            "narzędzia-dla-programistów",
            "wirtualna-i-rozszerzona-rzeczywistosc",
            "programowanie-aplikacji-mobilnych",
            "robotyka-afektywna",
            "informatyka-afektywna",
            "programowanie-gier-komputerowych",
            "psychoinformatyka",
            "informatyka-poznawcza",
            "seminaria-dyplomowe",
        ):
            subject_cards = [c for c in cards if f'href="{directory}/' in c]
            self.assertEqual(len(subject_cards), 1, directory)
        self.assertIn('class="materials-columns"', html)
        self.assertIn('text-decoration:none', html)
        self.assertNotRegex(html, r'<a\b[^>]*>Laboratorium\s')
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

    def test_compact_layout_uses_independent_columns(self):
        """Długie karty nie wymuszają pustej wysokości pozostałych."""
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn(".materials-grid{columns:4 260px;", style)
        self.assertIn("break-inside:avoid", style)
        self.assertIn(".materials-columns{display:block}", style)
        self.assertIn("column-count:2;column-gap:4px;column-fill:balance", style)
        self.assertIn(".materials-list--dense{column-count:3}", style)
        self.assertIn(".materials-list li{min-width:0;break-inside:avoid}", style)
        self.assertNotIn("grid-template-columns:repeat(", style)
        self.assertIn("materials-list--dense", html)
        self.assertIn("text-overflow:ellipsis", style)
        self.assertIn("@media(max-width:620px)", style)
        self.assertNotIn("grid-column:1/-1", style)

    def test_compact_subgroups_have_no_fill_and_small_margins(self):
        """Nagłówki podgrup są mniejsze, a wewnętrzne ramki przezroczyste."""
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn("h3{font-size:.5rem;", style)
        self.assertIn("margin:0 0 1px}", style)
        self.assertIn(".materials-subgroup{min-width:0;padding:2px 3px 3px;background:transparent;", style)
        self.assertIn("border:1px solid var(--subgroup-line);border-radius:5px;margin-top:2px}", style)
        self.assertIn("--subgroup-line:rgba(70,80,90,.14)", style)
        self.assertIn("--subgroup-line:rgba(205,215,230,.13)", style)
        self.assertIn("<h2>Wirtualna i rozszerzona rzeczywistość</h2>", html)
        self.assertNotIn("<h2>Wirtualna i rozszerzona rzeczywistość (WiRR)</h2>", html)
        self.assertIn("column-gap:8px;margin-top:8px", style)
        self.assertIn("margin:0 0 8px;break-inside:avoid", style)

    def test_subject_pages_have_valid_navigation(self):
        """Strony przedmiotów nie odsyłają do pustych lub usuniętych zasobów."""
        for subject in SUBJECTS:
            page = MATERIALS / subject / "index.html"
            html = page.read_text(encoding="utf-8")
            parser = Anchors()
            parser.feed(html)
            self.assertNotIn('href="#"', html, subject)
            for href in parser.links:
                with self.subTest(subject=subject, href=href):
                    self.assertTrue(href)
                    parts = urlsplit(href)
                    if parts.scheme or parts.netloc:
                        continue
                    self.assertNotEqual(href, "#")
                    target = (page.parent / unquote(parts.path)).resolve()
                    self.assertTrue(target.is_relative_to(ROOT))
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), href)
                    if parts.fragment:
                        target_html = target.read_text(encoding="utf-8")
                        self.assertIn(f'id="{unquote(parts.fragment)}"', target_html)
        robotics = (MATERIALS / "robotyka-afektywna" / "index.html")
        html = robotics.read_text(encoding="utf-8")
        for number in range(1, 8):
            filename = "ra_w01.pdf" if number == 1 else f"ra_w{number}.pdf"
            self.assertIn(f'href="{filename}"', html)

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
