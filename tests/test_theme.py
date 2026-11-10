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
                self.assertIn("setTimeout(() => root.classList.remove('theme-transition'), 1500)", page)
                self.assertIn("background-color 1.5s ease-in-out", page)
                self.assertIn("color 1.5s ease-in-out", page)
                self.assertIn("border-color 1.5s ease-in-out", page)
                self.assertIn("fill 1.5s ease-in-out", page)
                self.assertIn("stroke 1.5s ease-in-out", page)
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
        block = re.search(r'#badania \.research-intro\{([^}]+)\}', HTML)
        self.assertIsNotNone(block)
        for declaration in ("width:100%", "max-width:1000px", "margin-inline:auto",
                            "padding-inline:clamp(16px,2vw,24px)",
                            "font-size:.90rem", "line-height:1.65"):
            with self.subTest(declaration=declaration):
                self.assertIn(declaration, block.group(1))
        self.assertIn('#badania .research-heading{', HTML)
        self.assertIn('font-size:1.14rem', HTML)
        self.assertIn('border-inline-start:2px solid var(--accent)', HTML)
        self.assertIn('#badania .research-intro a{color:var(--accent)', HTML)
        self.assertIn('#badania .research-intro blockquote{border-inline-start:2px solid var(--accent)', HTML)

    def test_section_entrance_animation_is_scoped_and_accessible(self):
        """Sekcje i akapity wchodzą płynnie, z możliwością redukcji ruchu."""
        self.assertIn('@keyframes section-text-enter{', HTML)
        self.assertIn('from{opacity:0;transform:translateY(8px)}', HTML)
        self.assertIn('to{opacity:1;transform:translateY(0)}', HTML)
        self.assertIn('.panel.active:not(#badania){', HTML)
        self.assertIn('#badania.active .research-intro > *{', HTML)
        self.assertEqual(HTML.count('animation:section-text-enter 300ms'), 2)
        for index, delay in enumerate(range(40, 201, 40), start=2):
            self.assertIn(
                f'#badania.active .research-intro > :nth-child({index})'
                f'{{animation-delay:{delay}ms}}',
                HTML,
            )
        self.assertIn('@media(prefers-reduced-motion:reduce){', HTML)
        self.assertRegex(
            HTML,
            r'@media\(prefers-reduced-motion:reduce\)\{\s*'
            r'\.panel\.active:not\(#badania\),\s*'
            r'#badania\.active \.research-intro > \*\{animation:none\}',
        )
        self.assertIn("panels.forEach(p=>p.classList.toggle('active',p.id===id))", HTML)

    def test_research_biography_is_complete(self):
        """Opis zachowuje spójną narrację bez powtórzeń i skraca oryginał."""
        import json
        data = json.loads((ROOT / "docs/data/about.json").read_text(encoding="utf-8"))
        self.assertEqual(set(data), {"pl", "en"})
        self.assertEqual(data["pl"]["title"], "O mnie")
        self.assertEqual(data["en"]["title"], "About me")
        for language in ("pl", "en"):
            with self.subTest(language=language):
                paragraphs = data[language]["paragraphs"]
                self.assertEqual(len(paragraphs), 5)
                self.assertTrue(all(isinstance(p, str) and len(p.strip()) > 80
                                    for p in paragraphs))
                words = len(" ".join(paragraphs).split())
                self.assertGreater(words, 290)
                self.assertLess(words, 550)

        paragraphs = data["pl"]["paragraphs"]
        self.assertTrue(paragraphs[0].startswith(
            "Gdy ktoś pyta mnie, czym się zajmuję"))
        self.assertIn("Wszechświata", paragraphs[1])
        self.assertIn("ludzki mózg", paragraphs[2])
        self.assertIn("czujnik termiczny czy lidar", paragraphs[1])
        self.assertIn("Instytucie Optoelektroniki Wojskowej Akademii Technicznej",
                      paragraphs[3])
        self.assertIn("Politechniki Rzeszowskiej", paragraphs[4])
        self.assertIn("okulografii, EEG", paragraphs[4])
        self.assertIn("Największą satysfakcję", paragraphs[4])

    def test_research_biography_renders_without_embedded_prose(self):
        panel = re.search(
            r'<article class="panel" id="badania"[^>]*>([\s\S]*?)</article>',
            HTML,
        )
        self.assertIsNotNone(panel)
        content = panel.group(1)
        self.assertIn('id="research-status"', content)
        self.assertIn('id="research-intro"', content)
        self.assertNotIn('id="research-work"', content)
        self.assertNotIn('id="research-summary"', content)
        self.assertIn("fetch('docs/data/about.json')", HTML)
        self.assertIn("makeElement('h3','research-heading',description.title)", HTML)
        self.assertIn("description.paragraphs.forEach", HTML)
        self.assertNotIn('Gdy ktoś pyta mnie, czym się zajmuję', HTML)
        self.assertNotIn('<a ', content)

    def test_contact_links_have_icons(self):
        import re
        section = re.search(r'<article class="panel" id="kontakt"[\s\S]*?</article>', HTML)
        self.assertIsNotNone(section)
        self.assertEqual(section.group(0).count('class="link-icon'), 6)
        self.assertEqual(section.group(0).count('aria-hidden="true"'), 6)
        for text, url in (
            ("GitHub", "https://github.com/MatPomGit"),
            ("ORCID", "https://orcid.org/0000-0001-7769-8919"),
            ("Profil uczelniany", "https://mpomianek.v.prz.edu.pl/"),
            ("Google Scholar", "https://scholar.google.com/citations?user=B_NDcwsAAAAJ&amp;hl=pl"),
            ("LinkedIn", "https://www.linkedin.com/in/mateusz-pomianek-136455168"),
            ("Ludzie Nauki", "https://ludzie.nauka.gov.pl/ln/profiles/mateusz.pomianek.cwqxhvIDAOX"),
        ):
            self.assertIn(url, section.group(0))
            self.assertIn("<span>" + text + "</span>", section.group(0))
            self.assertRegex(
                section.group(0),
                re.escape('href="' + url + '"') + r' target="_blank" rel="noopener noreferrer"',
            )

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
        self.assertIn("v1.2.20", HTML)


if __name__ == "__main__":
    unittest.main()
