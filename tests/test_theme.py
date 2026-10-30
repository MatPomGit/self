"""Statyczne testy przelacznika i podstawowej palety kontrastu."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

HTML = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")


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

    def test_version(self):
        self.assertIn("v1.2.6", HTML)


if __name__ == "__main__":
    unittest.main()
