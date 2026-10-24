"""Offline regression tests for static resource routing and manifest."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_library", ROOT / "tools/build_library.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "assets/library.json").read_text(encoding="utf-8"))

    def test_manifest_has_version_and_entries(self):
        self.assertEqual(self.data["version"], 1)
        self.assertTrue(self.data["entries"])
        MODULE.validate(self.data["entries"])

    def test_aliases_exist_and_are_reproducible(self):
        for entry in self.data["entries"]:
            with self.subTest(entry=entry["type"] + "/" + entry["id"]):
                path = ROOT / entry["type"] / entry["id"] / "index.html"
                self.assertEqual(path.read_text(encoding="utf-8"), MODULE.page(entry["type"], entry["id"]))

    def test_duplicate_alias_rejected(self):
        example = dict(self.data["entries"][0])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            MODULE.validate([example, example])

    def test_unsafe_sources_rejected(self):
        example = dict(self.data["entries"][0])
        for source in ("../README.md", "/etc/passwd", "http://example.com/file.pdf",
                       "javascript:alert(1)", "downloads/missing.pdf"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    MODULE.validate([dict(example, source=source)])

    def test_invalid_identifiers_rejected(self):
        example = dict(self.data["entries"][0])
        for bad in ("1", "a", "../../", "01/02", ""):
            with self.subTest(id=bad):
                with self.assertRaises(ValueError):
                    MODULE.validate([dict(example, id=bad)])


if __name__ == "__main__":
    unittest.main()
