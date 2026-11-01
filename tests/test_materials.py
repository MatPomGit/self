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
        self.assertEqual(len(cards), 17)
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
            "Kto-Co-Jak",
            "Nowoczesne-technologie-w-psychologii",
            "analiza-eeg",
            "diagnoza-psychologiczna",
            "nawigacja-robotow-humanoidalnych",
            "neuropsychologia",
            "psychologia-poznawcza",
            "inne",
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


    def test_subject_order_and_file_colors(self):
        """Pokrewne przedmioty sąsiadują, a typ materiału ma własny kolor."""
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        titles = re.findall(r"<h4>([^<]+)</h4>", html)
        self.assertEqual(titles, [
            "Narzędzia dla programistów",
            "Programowanie aplikacji mobilnych",
            "Programowanie gier komputerowych",
            "Wirtualna i rozszerzona rzeczywistość",
            "Nawigacja robotów humanoidalnych",
            "Robotyka afektywna",
            "Informatyka afektywna",
            "Informatyka poznawcza",
            "Psychoinformatyka",
            "Analiza EEG",
            "Neuropsychologia",
            "Psychologia poznawcza",
            "Diagnoza psychologiczna",
            "Nowoczesne technologie w psychologii",
            "Seminaria dyplomowe",
            "Kto, co, jak",
            "Pozostałe",
        ])
        for selector in (
            ".materials-list a.material-link--lecture",
            ".materials-list a.material-link--lab",
        ):
            self.assertIn(selector, html)
        for variable in ("--lecture:", "--lab:", "--heading:"):
            self.assertEqual(len(re.findall(re.escape(variable) + r"#[0-9a-fA-F]{6}", html)), 2)
        self.assertIn('font-size:.86rem;line-height:1.15;font-weight:700;color:var(--heading)', html)
        for expected in (
            'class="material-link--lab" href="narzędzia-dla-programistów/ndp__lab__01.pdf"',
            'class="material-link--lab" href="analiza-eeg/lab1_wprowadzenie.pdf"',
            'class="material-link--lab" href="diagnoza-psychologiczna/diagnoza_lab1.docx"',
            'class="material-link--lecture" href="programowanie-aplikacji-mobilnych/pam_w01_intro.pdf"',
            'class="material-link--lecture" href="robotyka-afektywna/ra_w2.pdf"',
            'class="material-link--lecture" href="nawigacja-robotow-humanoidalnych/robo_w01.pptx"',
        ):
            self.assertIn(expected, html)

    def test_pptx_links_are_dark_orange_in_both_themes(self):
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn("--pptx:#9b4400", style)
        self.assertIn("--pptx:#f0a14a", style)
        self.assertIn('a[href$=".pptx" i]:visited{color:var(--pptx)}', style)
        self.assertRegex(html, r'href="[^"]+\.pptx"')

    def test_compact_layout_uses_independent_columns(self):
        """Długie karty nie wymuszają pustej wysokości pozostałych."""
        html = (MATERIALS / "index.html").read_text(encoding="utf-8")
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn(".materials-grid{columns:4 260px;", style)
        self.assertIn("break-inside:avoid", style)
        self.assertIn(".materials-columns{display:block}", style)
        self.assertIn("column-count:2;column-gap:4px;column-fill:balance", style)
        dense_columns = re.search(r"\.materials-list--dense\{column-count:(\d+)", style)
        self.assertIsNotNone(dense_columns)
        self.assertGreaterEqual(int(dense_columns.group(1)), 3)
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
        self.assertIn("h5{font-size:.5rem;", style)
        headings = re.findall(r'<div class="materials-subgroup">\s*<h([1-6])>', html)
        self.assertTrue(headings)
        self.assertEqual(set(headings), {"5"})
        self.assertIn("margin:0 0 1px}", style)
        subgroup = re.search(r"\.materials-subgroup\{([^}]+)\}", style)
        self.assertIsNotNone(subgroup)
        self.assertIn("background:transparent", subgroup.group(1))
        self.assertIn("padding:2px 2px 2px", subgroup.group(1))
        self.assertIn("border:1px solid var(--subgroup-line)", subgroup.group(1))
        self.assertIn("margin-top:2px", subgroup.group(1))
        self.assertIn("--subgroup-line:rgba(70,80,90,.14)", style)
        self.assertIn("--subgroup-line:rgba(205,215,230,.13)", style)
        self.assertRegex(html, r"<h[2-5]>Wirtualna i rozszerzona rzeczywistość</h[2-5]>")
        self.assertNotIn("Wirtualna i rozszerzona rzeczywistość (WiRR)", html)
        grid_spacing = re.search(
            r"\.materials-grid\{columns:\d+ \d+px;column-gap:(\d+)px;margin-top:(\d+)px\}",
            style,
        )
        self.assertIsNotNone(grid_spacing)
        self.assertTrue(all(int(value) <= 8 for value in grid_spacing.groups()))
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
