"""Ensure local links in source HTML resolve before CI repairs the materials index."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src", "poster"} and value:
                self.references.append(value)


class SourceLinksTests(unittest.TestCase):
    def test_local_html_links_resolve_in_repository(self):
        pages = [ROOT / "index.html", *sorted(p for p in (ROOT / "files").rglob("*.html")
                 if p.relative_to(ROOT / "files").parts[0] != "ignored")]
        for page in pages:
            parser = References()
            parser.feed(page.read_text(encoding="utf-8"))
            for reference in parser.references:
                part = urlsplit(reference)
                if part.scheme or part.netloc or not part.path:
                    continue
                rel = unquote(part.path)
                if rel.startswith("/self/"):
                    target = ROOT / rel.removeprefix("/self/")
                elif rel.startswith("/"):
                    target = ROOT / rel.lstrip("/")
                else:
                    target = page.parent / rel
                target = target.resolve()
                with self.subTest(page=page.relative_to(ROOT), link=reference):
                    self.assertTrue(target.is_relative_to(ROOT), "Link leaves repository")
                    self.assertTrue(
                        target.is_file() or (target / "index.html").is_file(),
                        "Local resource does not exist",
                    )


if __name__ == "__main__":
    unittest.main()
