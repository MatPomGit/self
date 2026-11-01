"""Regressions for automatic, deterministic materials index reconciliation."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.sync_materials import render


BASE = """<html>
<div class="materials-grid">
<section class="materials-group">
<h4>Example</h4>
<ul class="materials-list">
<li><a href="example/existing.pdf" download>existing</a></li>
</ul>
</section>
</div>

<script>
</script>
</html>
"""


class MaterialsSyncTests(unittest.TestCase):
    def make_root(self, path):
        materials = Path(path)
        subject = materials / "example"
        subject.mkdir()
        (subject / "existing.pdf").write_bytes(b"fixture")
        return materials

    def test_new_file_is_added_to_existing_subject_and_rebuild_is_stable(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            (root / "example" / "new_v1.0.pdf").write_bytes(b"fixture")
            output, issues = render(BASE, root)
            self.assertFalse(issues)
            self.assertIn('href="example/new_v1.0.pdf"', output)
            self.assertEqual(output.count("AUTO MATERIALS BEGIN"), 1)
            self.assertEqual(render(output, root), (output, []))
            (root / "example" / "new_v1.0.pdf").unlink()
            restored, issues = render(output, root)
            self.assertFalse(issues)
            self.assertNotIn("new_v1.0.pdf", restored)
            self.assertEqual(render(restored, root), (restored, []))

    def test_unknown_subject_gets_new_card_and_html_is_escaped(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            subject = root / "new-course"
            subject.mkdir()
            (subject / 'notes & "slides".pdf').write_bytes(b"fixture")
            output, issues = render(BASE, root)
            self.assertFalse(issues)
            self.assertIn("<h4>New course</h4>", output)
            self.assertIn('href="new-course/notes%20%26%20%22slides%22.pdf"', output)
            self.assertIn("notes &amp; &quot;slides&quot;", output)
            self.assertEqual(render(output, root), (output, []))

    def test_moved_and_renamed_reference_is_repaired(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            (root / "example" / "existing.pdf").unlink()
            nested = root / "example" / "presentations"
            nested.mkdir()
            (nested / "existing.pdf").write_bytes(b"fixture")
            (nested / "lecture_2026.pdf").write_bytes(b"fixture")
            source = BASE.replace("example/existing.pdf", "example/existing.pdf")
            fixed, issues = render(source, root)
            self.assertFalse(issues)
            self.assertIn('href="example/presentations/existing.pdf"', fixed)
            self.assertIn('href="example/presentations/lecture_2026.pdf"', fixed)

    def test_ambiguous_or_unresolved_reference_fails_closed(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            (root / "example" / "existing.pdf").unlink()
            broken, issues = render(BASE, root)
            self.assertTrue(any("Missing/ambiguous" in error for error in issues))
            self.assertIn('href="example/existing.pdf"', broken)

    def test_generated_index_pages_use_directory_url(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            other = root / "another"
            other.mkdir()
            (other / "index.html").write_text("<!doctype html>", encoding="utf-8")
            generated, issues = render(BASE, root)
            self.assertFalse(issues)
            self.assertIn('href="another/"', generated)
            self.assertEqual(render(generated, root), (generated, []))


if __name__ == "__main__":
    unittest.main()
