"""Statyczne testy przelacznika i podstawowej palety kontrastu."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
MATERIALS_HTML = (ROOT / "materials" / "index.html").read_text(encoding="utf-8")


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buttons = []

    def handle_starttag(self, tag, attrs):
        if tag == "button":
            self.buttons.append(dict(attrs))


def luminance(hex_color):
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    return sum(a * b for a, b in zip(rgb, (.2126, .7152, .0722)))


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + .05) / (low + .05)


class ThemeTests(unittest.TestCase):
    def test_button_accessibility(self):
        parser = Parser()
        parser.feed(HTML)
        buttons = [b for b in parser.buttons if b.get("id") == "theme-toggle"]
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].get("type"), "button")
        self.assertEqual(buttons[0].get("aria-label"), "Tryb ciemny")
        self.assertEqual(buttons[0].get("aria-pressed"), "false")

    def test_preference_persistence(self):
        for token in ("localStorage.getItem('self-theme')",
                      "localStorage.setItem('self-theme', next)",
                      "prefers-color-scheme: dark",
                      "themeToggle.addEventListener('click'",
                      "systemTheme.addEventListener('change'",
                      "themeToggle.setAttribute('aria-pressed', String(dark))"):
            with self.subTest(token=token):
                self.assertIn(token, HTML)
        self.assertLess(HTML.index("document.documentElement.dataset.theme ="),
                        HTML.index("<style>"))

    def test_theme_change_uses_smooth_colors_and_reduced_motion(self):
        for page in (HTML, MATERIALS_HTML):
            with self.subTest(page="home" if page is HTML else "materials"):
                self.assertIn("function changeTheme(next)", page)
                self.assertIn("root.classList.add('theme-transition')", page)
                self.assertIn("root.classList.remove('theme-transition')", page)
                self.assertIn("setTimeout(() => root.classList.remove('theme-transition'), 2500)", page)
                self.assertIn("background-color 2.5s ease-in-out", page)
                self.assertIn("color 2.5s ease-in-out", page)
                self.assertIn("border-color 2.5s ease-in-out", page)
                self.assertIn("fill 2.5s ease-in-out", page)
                self.assertIn("stroke 2.5s ease-in-out", page)
                self.assertIn("@media(prefers-reduced-motion:reduce)", page)
                self.assertIn("theme-transition body *::after {transition:none}", page)
                self.assertIn("changeTheme(next);", page)
                self.assertIn("changeTheme(event.matches ? 'dark' : 'light');", page)
                self.assertLess(page.index("document.documentElement.dataset.theme ="),
                                page.index("<style>"))

    def test_dark_palette(self):
        css = re.search(r':root\[data-theme="dark"\]\s*\{([^}]+)\}', HTML)
        self.assertIsNotNone(css)
        self.assertNotIn("#000", css.group(1))
        self.assertNotIn("#fff", css.group(1))
        self.assertIn("--surface:#202a35", css.group(1))
        self.assertIn("fill:var(--surface)", HTML)
        self.assertIn("fill:var(--on-accent)", HTML)

    def test_wcag_aa_palette(self):
        for fg, bg in (
            ("#e5eaf0", "#171c24"), ("#b2bdc8", "#171c24"),
            ("#b2bdc8", "#202a35"), ("#93c2e6", "#171c24"),
            ("#15202b", "#93c2e6"),
        ):
            with self.subTest(fg=fg, bg=bg):
                self.assertGreaterEqual(contrast(fg, bg), 4.5)

    def test_section_headings_are_in_shared_header(self):
        self.assertIn('<h1 class="header-section" id="header-section" hidden>', HTML)
        self.assertIn("headerSection.textContent='/ '+tr(sectionLabels[id])", HTML)
        self.assertIn("history.replaceState(null,'',location.pathname+location.search+`#${id}`);", HTML)
        for key, label in (("projekty", "Projekty"), ("badania", "Badania"),
                           ("kontakt", "Kontakt"), ("publikacje", "Publikacje")):
            self.assertIn(key + ":'" + label + "'", HTML)
        for redundant in ("<h2>Projekty</h2>", "<h2>Kontakt</h2>",
                          "<h2>Badania i działalność naukowa</h2>"):
            self.assertNotIn(redundant, HTML)

    def test_materials_theme_has_same_preference(self):
        parser = Parser()
        parser.feed(MATERIALS_HTML)
        toggles = [b for b in parser.buttons if b.get("id") == "theme-toggle"]
        self.assertEqual(len(toggles), 1)
        self.assertEqual(toggles[0].get("aria-pressed"), "false")
        for script in ("localStorage.getItem('self-theme')",
                       "localStorage.setItem('self-theme', next)",
                       "prefers-color-scheme: dark",
                       "themeToggle.addEventListener('click'",
                       "systemTheme.addEventListener('change'",
                       "themeToggle.setAttribute('aria-pressed', String(dark))"):
            with self.subTest(script=script):
                self.assertIn(script, MATERIALS_HTML)
        self.assertLess(MATERIALS_HTML.index("document.documentElement.dataset.theme ="),
                        MATERIALS_HTML.index("<style>"))
        self.assertIn('--accent:#93c2e6', MATERIALS_HTML)
        self.assertIn('--surface:#202a35', MATERIALS_HTML)

    def test_home_title_and_position(self):
        self.assertIn('transform:translateY(-98px)', HTML)
        self.assertIn('class="title-robotics">robotyka humanoidalna</span>', HTML)
        self.assertIn('white-space:nowrap', HTML)
        self.assertIn('max-height:690px', HTML)

    def test_research_typography(self):
        self.assertIn('#badania .research-intro{font-size:.94rem', HTML)
        self.assertIn('#badania .research-heading{font-size:1.14rem', HTML)

    def test_contact_links_have_icons(self):
        import re
        section = re.search(r'<article class="panel" id="kontakt"[\s\S]*?</article>', HTML)
        self.assertIsNotNone(section)
        self.assertEqual(section.group(0).count('class="link-icon'), 3)
        self.assertEqual(section.group(0).count('aria-hidden="true"'), 3)
        for text, url in (
            ("GitHub", "https://github.com/MatPomGit"),
            ("ORCID", "https://orcid.org/0000-0001-7769-8919"),
            ("Profil uczelniany", "https://mpomianek.v.prz.edu.pl/"),
        ):
            self.assertIn(url, section.group(0))
            self.assertIn("<span>" + text + "</span>", section.group(0))

    def test_work_in_progress_filter_matches_wheel(self):
        self.assertNotIn(">Cytowania</text>", HTML)
        self.assertIn('data-filter="progress">', HTML)
        self.assertIn('>Robocze</text>', HTML)
        self.assertIn('data-filter="progress" aria-pressed="false">Robocze</button>', HTML)
        self.assertIn("if(el.dataset.filter)", HTML)
        for name in ("all", "journal", "conference", "patent", "progress"):
            self.assertIn('data-filter="' + name + '">', HTML)

    def test_publication_actions_aligned_with_title(self):
        self.assertIn('.publication-heading{display:flex;align-items:flex-start;', HTML)
        self.assertIn('justify-content:flex-end;flex:0 0 auto;', HTML)
        self.assertIn('margin-left:auto}', HTML)
        self.assertIn("const heading=makeElement('div','publication-heading');", HTML)
        self.assertIn("heading.append(name,actions);", HTML)
        self.assertIn("body.append(heading,meta);", HTML)
        self.assertIn("item.append(body);fragment.append(item);", HTML)
        self.assertNotIn("item.append(body,actions)", HTML)

    def test_next_step_is_inline_after_project(self):
        self.assertIn("const next=makeElement('span','manuscript-next'", HTML)
        self.assertIn("project.append(projectLink,document.createTextNode(', '),next);", HTML)
        self.assertIn("item.append(heading,meta,description);list.append(item);", HTML)
        self.assertNotIn("item.append(heading,meta,description,next)", HTML)
        self.assertIn('.manuscript-next{font-size:inherit;line-height:inherit;', HTML)

    def test_version(self):
        self.assertIn("v1.2.11", HTML)


if __name__ == "__main__":
    unittest.main()
