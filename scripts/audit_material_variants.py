#!/usr/bin/env python3
"""Read-only inventory of potential material variants; never declares semantic duplicates."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

EXTENSIONS = {".pdf", ".docx", ".odt", ".pptx", ".tex", ".html"}
FORMAT_FAMILIES = [
    ("pdf_docx", {".pdf", ".docx"}),
    ("pdf_tex", {".pdf", ".tex"}),
    ("pdf_pptx", {".pdf", ".pptx"}),
]


def inventory(root: Path) -> dict:
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS
        and "ignored" not in p.relative_to(root).parts
    )
    by_stem = defaultdict(list)
    for path in files:
        key = (path.parent.relative_to(root).as_posix(), path.stem.casefold())
        by_stem[key].append(path)

    variants = []
    for (folder, stem), paths in sorted(by_stem.items()):
        suffixes = {p.suffix.lower() for p in paths}
        for family, extensions in FORMAT_FAMILIES:
            if extensions <= suffixes:
                variants.append({
                    "type": "FORMAT_VARIANT_CANDIDATE",
                    "family": family,
                    "files": sorted(p.relative_to(root).as_posix() for p in paths if p.suffix.lower() in extensions),
                    "decision": "UNVERIFIED",
                })

    # Same numbered tasks across the two WiRR series are an intentional
    # *comparison target*, not evidence of duplication.
    xr = root / "wirtualna-i-rozszerzona-rzeczywistosc"
    xr_pairs = []
    for number in range(1, 8):
        a = xr / f"wirr_lab_{number:02d}.pdf"
        b = xr / f"Lab_{number}_XR.pdf"
        if a.is_file() and b.is_file():
            xr_pairs.append({
                "type": "CROSS_SERIES_CANDIDATE",
                "files": [a.relative_to(root).as_posix(), b.relative_to(root).as_posix()],
                "decision": "REVIEW_REQUIRED",
                "note": "Primary laboratory vs additional XR exercise; compare learning objectives first.",
            })
    return {
        "schema_version": "1.0.0",
        "scope": "files/",
        "scanned_supported_files": len(files),
        "format_variants": variants,
        "cross_series_pairs": xr_pairs,
        "limitations": [
            "Filename and directory inventory only; no PDF/DOCX/PPTX semantic extraction.",
            "Do not infer MERGE or SUPERSEDE from a shared stem or number.",
            "files/ignored/ excluded recursively; never publish archive in Pages.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("files"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.root)
    output = args.output.resolve()
    source = args.root.resolve()
    if output == source or source in output.parents:
        parser.error("Audit output cannot be inside the public files/ tree")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Supported files: {report['scanned_supported_files']}; "
          f"format pairs: {len(report['format_variants'])}; "
          f"XR pairs: {len(report['cross_series_pairs'])}")


if __name__ == "__main__":
    main()
