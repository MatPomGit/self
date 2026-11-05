#!/usr/bin/env python3
"""Preflight for materials distributed with the static GitHub Pages site.

In CI only, malformed files are quarantined in the runner's temporary directory,
so they cannot appear in the generated index or published artifact. The original
Git repository is never modified; warnings document every excluded file.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "materials"
DOCUMENT_PARTS = {
    ".docx": "word/document.xml",
    ".pptx": "ppt/presentation.xml",
    ".odp": "content.xml",
}


def problem(path: Path) -> str | None:
    """Return an actionable reason for an obviously invalid document."""
    suffix = path.suffix.casefold()
    if suffix not in {".pdf", *DOCUMENT_PARTS}:
        return None
    try:
        if path.stat().st_size < 16:
            return "empty/truncated document"
        if suffix == ".pdf":
            with path.open("rb") as stream:
                header = stream.read(1024)
                stream.seek(max(0, path.stat().st_size - 4096))
                trailer = stream.read()
            if b"%PDF-" not in header:
                return "missing PDF header"
            if b"%%EOF" not in trailer:
                return "missing PDF EOF marker"
            return None
        with ZipFile(path) as archive:
            if DOCUMENT_PARTS[suffix] not in archive.namelist():
                return f"missing {DOCUMENT_PARTS[suffix]} package part"
    except (OSError, BadZipFile, ValueError) as exc:
        return f"unreadable document ({type(exc).__name__})"
    return None


def scan(materials: Path) -> list[tuple[Path, str]]:
    """Return bad files in stable path order, ignoring symlinks and hidden files."""
    return [
        (path.relative_to(materials), issue)
        for path in sorted(materials.rglob("*"))
        if path.is_file() and not path.is_symlink()
        and not any(part.startswith(".") for part in path.relative_to(materials).parts)
        if (issue := problem(path)) is not None
    ]


def quarantine(materials: Path, destination: Path, issues: list[tuple[Path, str]]) -> None:
    """Move invalid artifacts only in an ephemeral workspace, not from Git history."""
    if destination.resolve().is_relative_to(materials.resolve()):
        raise ValueError("Quarantine must be outside materials/")
    for relative, _ in issues:
        source = materials / relative
        target = destination / relative
        if target.exists():
            raise FileExistsError(f"Quarantine already contains {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true",
                      help="Report invalid files, fail without changing data")
    mode.add_argument("--quarantine", action="store_true",
                      help="Only in GitHub Actions: exclude invalid files from the build")
    args = parser.parse_args()
    if args.quarantine and (os.getenv("GITHUB_ACTIONS") != "true" or not os.getenv("RUNNER_TEMP")):
        parser.error("--quarantine is restricted to GitHub Actions ephemeral runners")
    issues = scan(MATERIALS)
    for relative, reason in issues:
        message = f"materials/{relative.as_posix()}: {reason}"
        print("[INVALID] " + message)
        if args.quarantine:
            safe_message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::warning::{safe_message}; omitted from published materials")
    if args.quarantine and issues:
        quarantine(MATERIALS, Path(os.environ["RUNNER_TEMP"]) / "self-invalid-materials", issues)
    print(f"[DONE] MATERIALS_PREFLIGHT;invalid={len(issues)};quarantined={len(issues) if args.quarantine else 0}")
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as output:
            output.write(f"\n### Materials preflight: {len(issues)} invalid file(s)\n")
            for relative, reason in issues:
                output.write(f"- \`{relative.as_posix()}\`: {reason}\n")
            if issues and args.quarantine:
                output.write("\nFiles above were excluded from the temporary build, not deleted from Git.\n")
    return int(bool(issues) and args.check)


if __name__ == "__main__":
    raise SystemExit(main())
