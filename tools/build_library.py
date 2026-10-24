#!/usr/bin/env python3
"""Generate canonical GitHub Pages aliases from assets/library.json (no dependencies)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"f", "p", "h"}
ID = re.compile(r"[0-9]{2,}\Z")


def validate(entries: list[dict], root: Path = ROOT) -> None:
    seen = set()
    for entry in entries:
        kind, ident = entry.get("type"), entry.get("id")
        if kind not in ALLOWED or not isinstance(ident, str) or not ID.fullmatch(ident):
            raise ValueError(f"Invalid type/id: {kind!r}/{ident!r}")
        key = (kind, ident)
        if key in seen:
            raise ValueError(f"Duplicate alias: {kind}/{ident}")
        seen.add(key)
        for name in ("title", "description", "category", "source"):
            if not isinstance(entry.get(name), str) or not entry[name].strip():
                raise ValueError(f"Missing {name} in {kind}/{ident}")
        status = entry.get("status", "ready")
        if status not in {"ready", "draft", "planned"}:
            raise ValueError(f"Invalid status in {kind}/{ident}: {status!r}")
        if status == "planned" and kind != "p":
            raise ValueError(f"Only PDF reservations are supported: {kind}/{ident}")
        src = entry["source"]
        if src.startswith("https://"):
            parsed = urlsplit(src)
            if not parsed.hostname or parsed.username or parsed.password:
                raise ValueError(f"Invalid HTTPS source: {src}")
        else:
            parts = PurePosixPath(src).parts
            if (
                not re.fullmatch(r"[A-Za-z0-9_./-]+", src)
                or src.startswith("/")
                or any(part in ("..", ".") for part in parts)
                or "//" in src
                or (status != "planned" and not (root / src).is_file())
            ):
                raise ValueError(f"Missing or unsafe local source: {src}")


def page(kind: str, ident: str) -> str:
    # All visible fields are set from validated JSON using textContent.
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index,follow">
<meta name="description" content="Podgląd dokumentu w bibliotece zasobów Mateusza Pomianka.">
<title>Zasób {kind}/{ident} | Biblioteka</title>
<link rel="stylesheet" href="../../assets/library.css">
<script defer src="../../assets/library.js"></script>
</head>
<body>
<div class="wrap">
<header><a href="../../">MP. / strona główna</a><nav class="toplinks" aria-label="Nawigacja"><a href="../../library/">Biblioteka</a><a href="../../materials.html">Materiały</a></nav></header>
<main data-library="reader" data-type="{kind}" data-id="{ident}">
<article class="reader">
<p><a href="../../library/">← Wróć do katalogu</a></p>
<h1 id="resource-title">Zasób {kind}/{ident}</h1>
<p class="muted" id="resource-description">Wczytywanie opisu zasobu...</p>
<div id="resource-meta"></div>
<div class="actions" id="resource-actions"></div>
<div id="resource-preview"></div>
</article>
</main>
<footer>Krótki adres: /self/{kind}/{ident} · GitHub Pages</footer>
</div>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without writing files")
    args = parser.parse_args()
    data = json.loads((ROOT / "assets/library.json").read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("entries"), list):
        raise ValueError("Unsupported manifest format")
    entries = data["entries"]
    validate(entries)
    for entry in entries:
        target = ROOT / entry["type"] / entry["id"] / "index.html"
        expected = page(entry["type"], entry["id"])
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Alias missing or out of date: {target.relative_to(ROOT)}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected, encoding="utf-8", newline="\n")
    print(f"LIBRARY_ALIASES={'VALID' if args.check else 'GENERATED'} ({len(entries)})")


if __name__ == "__main__":
    main()
