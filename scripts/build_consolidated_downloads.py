#!/usr/bin/env python3
"""Build canonical DOCX and PDF downloads from consolidated Markdown sources.

Only the four explicitly approved download paths may be written. Run locally or
in the PR-only CI publisher; no network calls. Pandoc + LibreOffice required.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = (
    ("analiza_afektywna", ROOT / "docs/consolidated/analiza_afektywna.md"),
    ("isaac_lab", ROOT / "docs/consolidated/isaac_lab.md"),
)
DEST = ROOT / "files/inne/analizy"
MIN_PDF_BYTES = 12_000
MIN_DOCX_BYTES = 8_000


def checked(command: list[str], *, timeout: int = 180) -> None:
    subprocess.run(command, check=True, timeout=timeout,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def validate(name: str, path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix == ".docx":
        if path.stat().st_size < MIN_DOCX_BYTES:
            raise ValueError(f"DOCX unexpectedly small: {path}")
        with ZipFile(path) as package:
            if "word/document.xml" not in package.namelist():
                raise ValueError(f"Not a valid DOCX: {path}")
            xml = package.read("word/document.xml")
            for required in (b"Streszczenie", b"Bibliografia"):
                if required not in xml:
                    raise ValueError(f"Missing editorial marker in DOCX {path}: {required}")
    elif path.suffix == ".pdf":
        if path.stat().st_size < MIN_PDF_BYTES:
            raise ValueError(f"PDF unexpectedly small: {path}")
        with path.open("rb") as stream:
            if not stream.read(5) == b"%PDF-":
                raise ValueError(f"Not a PDF: {path}")
            stream.seek(-4096, 2)
            if b"%%EOF" not in stream.read():
                raise ValueError(f"PDF lacks termination marker: {path}")
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        if not 2 <= len(reader.pages) <= 20:
            raise ValueError(f"Unexpected page count in {path}")
        text = " ".join(p.extract_text() or "" for p in reader.pages)
        if len(text) < 5000 or "Bibliografia" not in text:
            raise ValueError(f"PDF text extraction failed: {path}")


def build(root: Path = ROOT, *, output_dir: Path | None = None) -> list[Path]:
    destination = output_dir or root / "files/inne/analizy"
    destination = destination.resolve()
    if destination == root / "files/ignored" or destination.is_relative_to(root / "files/ignored"):
        raise ValueError("Canonical downloads cannot be written under files/ignored")
    if shutil.which("pandoc") is None or shutil.which("libreoffice") is None:
        raise RuntimeError("pandoc and LibreOffice Writer must be available")
    files: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="self-consolidated-") as temporary:
        temp = Path(temporary)
        profile = (temp / "lo-profile").as_uri()
        for name, relative in (
            ("analiza_afektywna", Path("docs/consolidated/analiza_afektywna.md")),
            ("isaac_lab", Path("docs/consolidated/isaac_lab.md")),
        ):
            source = root / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            docx = temp / f"{name}.docx"
            checked(["pandoc", str(source), "--from=gfm", "--to=docx",
                     "--standalone", "-M", "lang=pl-PL", "-o", str(docx)])
            checked(["libreoffice", f"-env:UserInstallation={profile}",
                     "--headless", "--convert-to", "pdf",
                     "--outdir", str(temp), str(docx)])
            pdf = temp / f"{name}.pdf"
            validate(name, docx)
            validate(name, pdf)
        destination.mkdir(parents=True, exist_ok=True)
        for name in ("analiza_afektywna", "isaac_lab"):
            for ext in (".docx", ".pdf"):
                source = temp / f"{name}{ext}"
                target = destination / source.name
                shutil.copyfile(source, target)
                files.append(target)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    files = build(ROOT, output_dir=args.output_dir)
    for f in files:
        print(f"[CONSOLIDATED] {f.relative_to(ROOT) if f.is_relative_to(ROOT) else f} "
              f"{f.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
