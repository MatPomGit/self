#!/usr/bin/env python3
"""Reconcile the static materials page with the current repository inventory.

Preserve hand-written descriptions and ordering. New files are appended to their
subject card during CI; no GitHub credentials or repository commits are needed.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from html import escape, unescape
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "materials" / "index.html"
CARD = re.compile(
    r'<section class="materials-group(?: materials-group--wide)?">[\s\S]*?</section>'
)
LINK = re.compile(r'(?P<before><a\b[^>]*\bhref=")(?P<href>[^"]+)(?P<after>")')
AUTO = re.compile(
    r'\n?<!-- AUTO MATERIALS BEGIN -->[\s\S]*?<!-- AUTO MATERIALS END -->\n?'
)
VERSION = re.compile(r'(?i)(?:[._-]v\d+(?:[._]\d+)*)$')


def inventory(materials: Path) -> dict[str, Path]:
    """Inventory regular public files, not the generated root index."""
    return {
        path.relative_to(materials).as_posix(): path
        for path in sorted(materials.rglob("*"))
        if path.is_file() and not path.is_symlink()
        and path != materials / "index.html"
        and not any(part.startswith(".") for part in path.relative_to(materials).parts)
    }


def file_key(name: str) -> str:
    stem = VERSION.sub("", Path(name).stem)
    return re.sub(r"[^a-z0-9]", "", stem.casefold()).replace("z2013", "2013")


def target_of(href: str, files: dict[str, Path]) -> str | None:
    part = urlsplit(unescape(href))
    if part.scheme or part.netloc or not part.path:
        return None
    relative = unquote(part.path).removeprefix("./")
    if relative.endswith("/"):
        relative += "index.html"
    return relative if relative in files else None


def relocated(href: str, files: dict[str, Path]) -> str | None:
    """Repair unique moves/renames within the same subject, never guess others."""
    current = unquote(urlsplit(unescape(href)).path).removeprefix("./")
    parts = Path(current).parts
    if not parts:
        return None
    subject = parts[0]
    basename = Path(current).name.casefold()
    candidates = [
        name for name in files
        if Path(name).parts[0] == subject
        and Path(name).name.casefold() == basename
    ]
    if len(candidates) == 1:
        return candidates[0]
    if candidates:
        return None
    key = file_key(current)
    suffix = Path(current).suffix.casefold()
    candidates = [
        name for name in files
        if Path(name).parts[0] == subject
        and Path(name).suffix.casefold() == suffix
        and file_key(name) == key
    ]
    return candidates[0] if len(candidates) == 1 else None


def href_for(name: str) -> str:
    if name.endswith("/index.html"):
        name = name[:-len("index.html")]
    return quote(name, safe="/-._~()")


def label_for(name: str) -> str:
    path = Path(name)
    if path.name == "index.html":
        return "Strona przedmiotu"
    return path.stem.replace("_", " ").replace("-", " ").strip() or path.name


def render(source: str, materials: Path) -> tuple[str, list[str]]:
    """Return deterministically regenerated HTML and actionable errors."""
    files = inventory(materials)
    source = AUTO.sub("\n", source)
    failures: list[str] = []
    seen: set[str] = set()
    subjects: set[str] = set()

    def update_card(match: re.Match[str]) -> str:
        card = match.group(0)
        paths: set[str] = set()

        def fix_link(m: re.Match[str]) -> str:
            href = m.group("href")
            part = urlsplit(unescape(href))
            if part.scheme or part.netloc or part.path.startswith("../"):
                failures.append(f"Unsupported link in materials card: {href}")
                return m.group(0)
            path = target_of(href, files)
            if path is None:
                path = relocated(href, files)
                if path is None:
                    failures.append(f"Missing/ambiguous material: {href}")
                    return m.group(0)
                href = href_for(path)
            seen.add(path)
            paths.add(path.split("/", 1)[0])
            return m.group("before") + escape(href, quote=True) + m.group("after")

        card = LINK.sub(fix_link, card)
        if len(paths) > 1:
            failures.append(f"Mixed subject paths in one materials card: {sorted(paths)}")
        subjects.update(paths)
        subject = next(iter(paths), None)
        if subject:
            missing = sorted(
                (name for name in files
                 if name.startswith(subject + "/") and name not in seen),
                key=str.casefold,
            )
            if missing:
                card = add_links(card, missing, subject)
                seen.update(missing)
        return card

    result = CARD.sub(update_card, source)
    remaining = sorted(
        (name for name in files if name not in seen), key=str.casefold
    )
    by_subject: dict[str, list[str]] = defaultdict(list)
    for name in remaining:
        by_subject[name.split("/", 1)[0]].append(name)
    if by_subject:
        new_cards = []
        for subject, names in sorted(by_subject.items(), key=lambda item: item[0].casefold()):
            title = escape(subject.replace("-", " ").replace("_", " ").capitalize())
            blank = f'<section class="materials-group">\n<h4>{title}</h4>\n</section>'
            new_cards.append(add_links(blank, names, subject))
        marker = "</div>\n\n<script>"
        if marker not in result:
            failures.append("Cannot locate end of materials grid")
        else:
            result = result.replace(marker, "\n".join(new_cards) + "\n" + marker, 1)
    if not CARD.search(source):
        failures.append("No materials cards found")
    return result, failures


def add_links(card: str, names: list[str], subject: str) -> str:
    grouped: dict[str, list[str]] = defaultdict(list)
    for name in names:
        remainder = Path(name).relative_to(subject)
        group = remainder.parent.as_posix()
        grouped[group].append(name)
    blocks = ["<!-- AUTO MATERIALS BEGIN -->"]
    for group, entries in sorted(grouped.items(), key=lambda item: item[0].casefold()):
        title = "Nowe materiały" if group == "." else group.replace("/", " / ").replace("-", " ").capitalize()
        blocks.extend([
            '<div class="materials-subgroup">',
            f"<h5>{escape(title)}</h5>",
            '<ul class="materials-list">',
        ])
        for name in entries:
            href = escape(href_for(name), quote=True)
            label = escape(label_for(name))
            blocks.append(f'<li><a href="{href}" download title="{escape(Path(name).name, quote=True)}">{label}</a></li>')
        blocks.extend(["</ul>", "</div>"])
    blocks.append("<!-- AUTO MATERIALS END -->")
    # Canonicalize whitespace before the generated block for repeatable builds.
    position = card.rfind("</section>")
    card = card[:position].rstrip() + card[position:]
    return card.replace("</section>", "\n" + "\n".join(blocks) + "\n</section>", 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = INDEX.read_text(encoding="utf-8")
    output, failures = render(source, INDEX.parent)
    for failure in failures:
        print("[FAIL] " + failure)
    if failures:
        print(f"[DONE] MATERIALS_INDEX_FAIL;issues={len(failures)}")
        return 1
    if args.check and output != source:
        print("[FAIL] MATERIALS_INDEX_STALE (run --write)")
        return 1
    if args.write and output != source:
        INDEX.write_text(output, encoding="utf-8")
    print(f"[DONE] MATERIALS_INDEX_PASS;files={len(inventory(INDEX.parent))};updated={output != source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
