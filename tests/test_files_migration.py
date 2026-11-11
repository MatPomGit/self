"""Regression checks for the public materials/ -> files/ migration."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class FilesMigrationTests(unittest.TestCase):
    def test_public_files_and_legacy_index(self):
        self.assertTrue((ROOT / "files" / "index.html").is_file())
        self.assertTrue((ROOT / "files" / "analiza-eeg" / "data").is_dir())
        legacy = (ROOT / "materials" / "index.html").read_text(encoding="utf-8")
        self.assertIn("../files/", legacy)
        self.assertFalse((ROOT / "materials" / "analiza-eeg").exists())

    def test_home_and_pipeline_use_new_path(self):
        page = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="files/"', page)
        self.assertNotIn('href="materials/"', page)
        workflow = (ROOT / ".github" / "workflows" / "restore-original-pages.yml").read_text(encoding="utf-8")
        self.assertIn("cp -a docs files materials _site/", workflow)
        self.assertIn("cp index.html 404.html _site/", workflow)

    def test_legacy_deep_links_have_browser_fallback(self):
        fallback = (ROOT / "404.html").read_text(encoding="utf-8")
        self.assertIn("'/materials/'", fallback)
        self.assertIn("'/files/'", fallback)
        self.assertIn("window.location.replace", fallback)

if __name__ == "__main__":
    unittest.main()
