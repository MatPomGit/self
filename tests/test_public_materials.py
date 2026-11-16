"""Regression contract shared by public inventory, preflight and PDF aliases."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from scripts.public_materials import is_public_material, public_material_files
from scripts.sync_materials import inventory
from scripts.build_short_links import pdf_routes
from scripts.preflight_materials import scan
from scripts.classify_materials import classify


class PublicMaterialsTests(unittest.TestCase):
    def test_inventory_excludes_archive_hidden_files_and_nested_hidden_directories(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / "files"
            for folder in ("course", "course/ignored", "course/.private",
                           "ignored/course", ".hidden/course"):
                (root / folder).mkdir(parents=True)
            for filename in (
                "course/lecture.pdf",
                "course/ignored/local.pdf",
                "course/.private/hidden.pdf",
                "ignored/course/obsolete.pdf",
                ".hidden/course/secret.pdf",
                ".hidden-file.pdf",
            ):
                (root / filename).write_bytes(b"%PDF-fixture")
            actual = [p.relative_to(root).as_posix() for p in public_material_files(root)]
            self.assertEqual(actual, ["course/ignored/local.pdf", "course/lecture.pdf"])
            self.assertEqual(sorted(inventory(root)), actual)
            self.assertEqual(sorted(pdf_routes(root)), actual)
            self.assertFalse(is_public_material(root, root / "ignored/course/obsolete.pdf"))
            self.assertFalse(is_public_material(root, root / "course/.private/hidden.pdf"))
            self.assertFalse(is_public_material(root, root / "course/../ignored/course/obsolete.pdf"))
            self.assertFalse(is_public_material(root, Path(temp) / "outside.pdf"))

    def test_symlinks_and_directory_symlinks_are_never_published(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / "files"
            course = root / "course"
            course.mkdir(parents=True)
            (course / "real.pdf").write_bytes(b"%PDF-fixture")
            external = Path(temp) / "outside"
            external.mkdir()
            (external / "private.pdf").write_bytes(b"%PDF-fixture")
            try:
                (course / "shortcut.pdf").symlink_to(course / "real.pdf")
                (root / "linked-folder").symlink_to(external, target_is_directory=True)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"Symlinks unavailable: {error}")
            expected = ["course/real.pdf"]
            self.assertEqual([p.relative_to(root).as_posix() for p in public_material_files(root)], expected)
            self.assertFalse(is_public_material(root, course / "shortcut.pdf"))
            self.assertFalse(is_public_material(root, root / "linked-folder/private.pdf"))
            self.assertEqual(sorted(pdf_routes(root)), expected)

    def test_preflight_only_scans_public_inputs(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / "files"
            (root / "course").mkdir(parents=True)
            (root / "ignored").mkdir()
            (root / "course" / "bad.pdf").write_bytes(b"invalid")
            (root / "ignored" / "bad.pdf").write_bytes(b"invalid")
            self.assertEqual([p.as_posix() for p, _ in scan(root)], ["course/bad.pdf"])

    def test_classifier_never_reads_archived_or_hidden_paths(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / "files"
            (root / "ignored").mkdir(parents=True)
            (root / ".hidden").mkdir()
            (root / "ignored" / "obsolete.pdf").write_bytes(b"%PDF-fixture")
            (root / ".hidden" / "secret.pdf").write_bytes(b"%PDF-fixture")
            html = ''.join(
                f'<li><a href="{name}">PDF</a></li>'
                for name in ("ignored/obsolete.pdf", ".hidden/secret.pdf",
                             "../outside.pdf", "https://example.org/external.pdf")
            )
            with patch("scripts.classify_materials.dimensions",
                       side_effect=AssertionError("Excluded file was opened")):
                output, changes = classify(html, root)
            self.assertEqual(output, html)
            self.assertEqual(changes, [])


if __name__ == "__main__":
    unittest.main()
