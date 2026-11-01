#!/usr/bin/env python3
"""Oznaczaj wykłady 16:9/4:3 i instrukcje A4 na podstawie plików."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

from pypdf import PdfReader
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "materials" / "index.html"
ANCHOR = re.compile(r'(<li>\s*<a)(?: class="([^"]*)")?(\s+href="([^"]+)"[^>]*>)')
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def kind(width: float, height: float) -> str | None:
    if min(width, height) <= 0:
        return None
    ratio = max(width, height) / min(width, height)
    if min(abs(ratio - 16 / 9), abs(ratio - 4 / 3)) <= .035:
        return "lecture"
    if abs(ratio - 297 / 210) <= .025:
        return "lab"
    return None


def dimensions(path: Path) -> tuple[float, float] | None:
    ext = path.suffix.lower()
    if ext == ".pdf":
        try:
            page = PdfReader(str(path), strict=False).pages[0]
            box = page.cropbox
            return float(box.width), float(box.height)
        except (OSError, ValueError, IndexError, KeyError):
            return None
    if ext not in (".pptx", ".docx"):
        return None
    try:
        with ZipFile(path) as package:
            if ext == ".pptx":
                root = ET.fromstring(package.read("ppt/presentation.xml"))
                size = root.find(f".//{{{P_NS}}}sldSz")
                if size is not None:
                    return float(size.attrib["cx"]), float(size.attrib["cy"])
            else:
                root = ET.fromstring(package.read("word/document.xml"))
                pages = list(root.iter(f"{{{W_NS}}}pgSz"))
                if pages:
                    return (float(pages[-1].attrib[f"{{{W_NS}}}w"]),
                            float(pages[-1].attrib[f"{{{W_NS}}}h"]))
    except (OSError, BadZipFile, KeyError, ValueError, ET.ParseError):
        return None
    return None


def classify(html: str, materials: Path) -> tuple[str, list[str]]:
    """Modyfikuj wyłącznie klasę linku; ścieżek i kolejności nie zmieniaj."""
    root = materials.resolve()
    cache: dict[Path, str | None] = {}
    changes: list[str] = []

    def get_type(path: Path) -> str | None:
        if path not in cache:
            size = dimensions(path)
            cache[path] = kind(*size) if size else None
        return cache[path]

    def process(match: re.Match[str]) -> str:
        start, old, rest, href = match.groups()
        path = (root / unquote(urlsplit(href).path)).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            return match[0]
        detected = get_type(path)
        if detected is None and path.suffix.lower() in (".html", ".tex"):
            pdf = path.with_suffix(".pdf")
            if pdf.is_file():
                detected = get_type(pdf)
        if detected is None:
            return match[0]
        names = old.split() if old else []
        new_names = [n for n in names if n not in ("material-link--lab", "material-link--lecture")]
        new_names.append("material-link--" + detected)
        updated = start + ' class="' + " ".join(new_names) + '"' + rest
        if updated != match[0]:
            changes.append(f"{detected}: {path.relative_to(root)}")
        return updated

    return ANCHOR.sub(process, html), changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    option = parser.add_mutually_exclusive_group(required=True)
    option.add_argument("--write", action="store_true")
    option.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = INDEX.read_text(encoding="utf-8")
    output, changes = classify(content, INDEX.parent)
    if args.check and output != content:
        print(f"[FAIL] MATERIALS_GEOMETRY_STALE;changes={len(changes)}")
        return 1
    if args.write and output != content:
        INDEX.write_text(output, encoding="utf-8")
        for change in changes:
            print("[MATERIAL] " + change)
    print(f"[DONE] MATERIALS_GEOMETRY_PASS;changes={len(changes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
