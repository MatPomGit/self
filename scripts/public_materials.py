"""Single source of truth for files eligible for public material processing.

`files/ignored/` is a repository archive, not a publishing input. Hidden
entries and symlinks are excluded as well. Walk prunes excluded directories
before entering them, rather than merely filtering the resulting filenames.
"""
from __future__ import annotations

import os
from pathlib import Path


def is_public_material(root: Path, path: Path) -> bool:
    """Whether a regular file is eligible for indexing, preflight or aliases."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    if (not relative.parts or relative.parts[0] == "ignored"
            or any(part.startswith(".") for part in relative.parts)):
        return False
    if not path.is_file() or path.is_symlink():
        return False
    if any((root.joinpath(*relative.parts[:index])).is_symlink()
           for index in range(1, len(relative.parts))):
        return False
    return path.resolve().is_relative_to(root.resolve())


def public_material_files(root: Path) -> list[Path]:
    """Return deterministic, sorted public files without traversing archives."""
    result: list[Path] = []
    for parent, directories, names in os.walk(root, topdown=True, followlinks=False):
        directory = Path(parent)
        directories[:] = [
            name for name in sorted(directories)
            if not name.startswith(".")
            and not (directory == root and name == "ignored")
            and not (directory / name).is_symlink()
        ]
        for name in names:
            path = directory / name
            if is_public_material(root, path):
                result.append(path)
    return sorted(result)
