"""Ensure the 404 page preserves portal design and legacy redirects."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "404.html").read_text(encoding="utf-8")


class Audit404(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.headings = []
        self.main = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag in ("h1", "h2", "h3"):
            self.headings.append((tag, attrs))
        if tag == "main":
            self.main += 1


class NotFoundPageTests(unittest.TestCase):
    def test_site_navigation_and_accessibility(self):
        parsed = Audit404()
        parsed.feed(PAGE)
        self.assertEqual(parsed.main, 1)
        self.assertTrue(all(tag == "h1" for tag, _ in parsed.headings))
        self.assertEqual(len(parsed.headings), 2, "Separate PL/EN main headings")
        self.assertIn("/", parsed.links)
        self.assertIn("/files/", parsed.links)
        self.assertIn("?lang=en", parsed.links)
        self.assertIn("?lang=pl", parsed.links)
        for token in ('aria-live="polite"', 'id="theme-toggle"',
                      'aria-pressed="false"', 'id="new-hypothesis"',
                      '@media(max-width:800px)', 'prefers-reduced-motion:reduce'):
            with self.subTest(token=token):
                self.assertIn(token, PAGE)

    def test_palettes_and_language_match_homepage(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        for token in ('--accent:#1d4f7a', '--accent:#93c2e6',
                      '--surface:#202a35', "localStorage.getItem('self-theme')"):
            self.assertIn(token, home)
            self.assertIn(token, PAGE)
        self.assertIn('data-lang-content="en"', PAGE)
        self.assertIn('data-lang-content="pl"', PAGE)
        self.assertIn('data-theme="dark"', PAGE)

    def test_redirect_guard_precedes_page_setup(self):
        self.assertIn("const legacy = '/materials/';", PAGE)
        self.assertIn("window.location.replace('/files/'", PAGE)
        self.assertIn("window.location.search + window.location.hash", PAGE)
        self.assertLess(PAGE.index("window.location.replace('/files/'"),
                        PAGE.index("document.documentElement.dataset.theme ="))
        self.assertIn('<meta name="robots" content="noindex,follow">', PAGE)


if __name__ == "__main__":
    unittest.main()
