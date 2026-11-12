#!/usr/bin/env python3
"""Build stable, short PDF viewing URLs for the static GitHub Pages site.

Original PDF files stay at their existing paths. Alias pages are generated in
the ephemeral publication artifact, not committed to the source materials.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
from html import escape, unescape
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote, unquote, urlsplit

COURSES = {
    "Kto-Co-Jak": "kcj",
    "analiza-eeg": "eeg",
    "diagnoza-psychologiczna": "diag",
    "informatyka-afektywna": "ia",
    "informatyka-poznawcza": "ip",
    "narzędzia-dla-programistów": "ndp",
    "nawigacja-robotow-humanoidalnych": "robo",
    "neuropsychologia": "neuro",
    "nowoczesne-technologie-w-psychologii": "ntp",
    "programowanie-aplikacji-mobilnych": "pam",
    "programowanie-gier-komputerowych": "pgk",
    "psychoinformatyka": "pi",
    "psychologia-poznawcza": "pp",
    "robotyka-afektywna": "ra",
    "seminaria-dyplomowe": "sd",
    "wirtualna-i-rozszerzona-rzeczywistosc": "wirr",
    "inne": "inne",
}
NUMBERED = re.compile(
    r"(?:^|[_ .-])(?P<kind>lab|w|wyklad|wykład)[_ .-]*(?P<number>\d{1,3})(?=$|[_ .-])",
    re.IGNORECASE,
)
ANCHOR = re.compile(r'<a\b[^>]*\bhref="(?P<href>[^"]+)"[^>]*>', re.IGNORECASE)


def slug(text: str, maximum: int = 32) -> str:
    text = text.translate(str.maketrans("łŁ", "lL"))
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    normalized = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-") or "plik"
    if len(normalized) <= maximum:
        return normalized
    digest = hashlib.sha256(normalized.encode()).hexdigest()[:5]
    return normalized[:maximum - 6].rstrip("-") + "-" + digest


def alias_base(relative: Path) -> tuple[str, str, str]:
    """Return (course prefix, short document slug, alternative suffix)."""
    subject = relative.parts[0]
    prefix = COURSES.get(subject, slug(subject))
    if subject == "inne" and len(relative.parts) > 2:
        prefix += "/" + slug(relative.parts[1])
    stem = relative.stem
    number = NUMBERED.search(stem)
    if number:
        kind = "lab" if number.group("kind").casefold() == "lab" else "w"
        code = f"{kind}{int(number.group('number')):02d}"
        tail = stem[number.end():].strip(" _.-")
        if re.search(r"(?:^|[_ .-])notes?(?:$|[_ .-])", tail, re.I):
            code += "-notes"
        return prefix, code, slug(tail, 18) if tail else slug(stem, 18)
    return prefix, slug(stem, 28), slug(stem, 18)


def ranked(relative: Path) -> tuple[int, int, str]:
    subject = relative.parts[0]
    prefix = COURSES.get(subject, slug(subject)).split("/")[-1]
    stem = relative.stem.lower()
    return (0 if stem.startswith(prefix + "_") or stem.startswith(prefix + "-") else 1,
            len(stem), relative.as_posix().casefold())


def pdf_routes(files: Path) -> dict[str, str]:
    """Map original PDF paths relative to files/ to short relative URLs."""
    pdfs = [
        path.relative_to(files) for path in files.rglob("*")
        if path.is_file() and not path.is_symlink() and path.suffix.casefold() == ".pdf"
        and path.relative_to(files).parts[0] != "ignored"
        and not any(part.startswith(".") for part in path.relative_to(files).parts)
    ]
    used: set[str] = set()
    routes: dict[str, str] = {}
    for relative in sorted(pdfs, key=ranked):
        prefix, code, suffix = alias_base(relative)
        candidate = f"{prefix}/{code}/"
        if candidate in used:
            candidate = f"{prefix}/{code}-{suffix}/"
        if candidate in used:
            digest = hashlib.sha256(relative.as_posix().encode()).hexdigest()[:7]
            candidate = f"{prefix}/{code}-{digest}/"
        if candidate in used:
            raise ValueError(f"Short URL collision for {relative}")
        destination = files / candidate / "index.html"
        # An existing course index or real file must never be overwritten.
        if destination.exists():
            raise ValueError(f"Short URL would overwrite {destination}")
        used.add(candidate)
        routes[relative.as_posix()] = candidate
    if len(routes) != len(pdfs):
        raise ValueError("Incomplete PDF alias mapping")
    return routes


def rewrite_index(document: str, routes: dict[str, str]) -> tuple[str, int]:
    """Change the displayed PDF link, retaining its source for JS downloads."""
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        tag = match.group()
        raw_href = match.group("href")
        parsed = urlsplit(unescape(raw_href))
        if parsed.scheme or parsed.netloc or not parsed.path:
            return tag
        source = unquote(parsed.path).removeprefix("./")
        short = routes.get(source)
        if short is None:
            return tag
        if "data-original-url=" in tag:
            raise ValueError(f"Already rewritten PDF link: {source}")
        replacement = f'href="{escape(short, quote=True)}" data-original-url="{raw_href}"'
        tag = tag.replace(f'href="{raw_href}"', replacement, 1)
        tag = re.sub(r'\s+download(?:="[^"]*")?(?=\s|>)', "", tag)
        count += 1
        return tag

    return ANCHOR.sub(replace, document), count


def viewer_html(path: str, short: str) -> str:
    filename = Path(path).name
    title = Path(path).stem.replace("_", " ").replace("-", " ")
    url = "/files/" + quote(path, safe="/-._~()")
    canonical = "https://matpom.pl/files/" + short
    safe_url = escape(url, quote=True)
    safe_title = escape(title)
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,follow">
<meta name="description" content="Podgląd materiału PDF: {escape(filename, quote=True)}">
<link rel="canonical" href="{escape(canonical, quote=True)}">
<title>{safe_title} · Materiały dydaktyczne</title>
<style>
:root{{color-scheme:light dark}}
*{{box-sizing:border-box}}
body{{margin:0;font:15px/1.4 system-ui,Arial,sans-serif;background:#f6f8fb;color:#17212e}}
header{{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:9px 18px;background:#1c304e;color:#fff}}
header strong{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
nav{{display:flex;flex-wrap:wrap;gap:12px;flex-shrink:0}}
a{{color:inherit;text-underline-offset:3px}}
iframe{{width:100%;height:calc(100dvh - 54px);display:block;border:0;background:white}}
@media(max-width:640px){{header{{align-items:flex-start;flex-direction:column}}iframe{{height:calc(100dvh - 100px)}}}}
</style>
</head>
<body>
<header>
<strong>{safe_title}</strong>
<nav>
<a href="/files/">Wszystkie materiały</a>
<a href="{safe_url}" download>Pobierz PDF</a>
<a href="{safe_url}" target="_blank" rel="noopener">Otwórz PDF</a>
</nav>
</header>
<iframe src="{safe_url}" title="Podgląd pliku PDF: {safe_title}"></iframe>
<noscript><p><a href="{safe_url}">Otwórz materiał PDF</a></p></noscript>
</body>
</html>
"""


def build(site: Path, *, check: bool = False) -> tuple[int, int]:
    site = site.resolve()
    files = site / "files"
    index = files / "index.html"
    if not index.is_file():
        raise FileNotFoundError(f"No materials index: {index}")
    routes = pdf_routes(files)
    updated, links = rewrite_index(index.read_text(encoding="utf-8"), routes)
    if links == 0 or not routes:
        raise ValueError("No PDF source links were found")
    if not check:
        index.write_text(updated, encoding="utf-8")
        for path, short in routes.items():
            destination = files / short / "index.html"
            destination.parent.mkdir(parents=True, exist_ok=False)
            destination.write_text(viewer_html(path, short), encoding="utf-8")
    return len(routes), links


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True, help="Root of the source or built site")
    parser.add_argument("--check", action="store_true", help="Validate mapping without modifying files")
    args = parser.parse_args()
    routes, links = build(args.site, check=args.check)
    print(f"[DONE] SHORT_PDF_URLS_PASS;routes={routes};linked={links};check={args.check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
