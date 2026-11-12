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

    def test_ignored_archive_never_appears_in_materials_index(self):
        with TemporaryDirectory() as temp:
            materials = self.make_root(temp)
            archived = materials / "ignored" / "example"
            archived.mkdir(parents=True)
            (archived / "legacy.pdf").write_bytes(b"%PDF-test-archive")
            (materials / "example" / "current.pdf").write_bytes(b"%PDF-test")
            result, issues = render(BASE, materials)
            self.assertFalse(issues)
            self.assertIn("example/current.pdf", result)
            self.assertNotIn("legacy.pdf", result)
            self.assertNotIn('data-materials-subject="ignored"', result)
            self.assertEqual(render(result, materials), (result, []))

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

    def test_ci_repair_prunes_only_stale_standalone_links(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            source = BASE.replace(
                "</ul>",
                '<li><a href="example/missing.html">old HTML</a></li>\n</ul>',
            )
            warnings = []
            output, failures = render(source, root, repair_missing=True, warnings=warnings)
            self.assertFalse(failures)
            self.assertNotIn("missing.html", output)
            self.assertIn('href="example/existing.pdf"', output)
            self.assertEqual(len(warnings), 1)
            self.assertEqual(render(output, root), (output, []))

    def test_ci_repair_fails_closed_on_ambiguous_rename(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            (root / "example" / "series_v1.pdf").write_bytes(b"fixture")
            (root / "example" / "series_v2.pdf").write_bytes(b"fixture")
            source = BASE.replace(
                "</ul>",
                '<li><a href="example/series.pdf">ambiguous</a></li>\n</ul>',
            )
            warnings = []
            output, failures = render(source, root, repair_missing=True, warnings=warnings)
            self.assertTrue(any("Missing/ambiguous material" in x for x in failures))
            self.assertIn('href="example/series.pdf"', output)
            self.assertEqual(warnings, [])

    def test_ci_repair_does_not_hide_unsupported_links(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            source = BASE.replace("example/existing.pdf", "../outside.pdf")
            _, failures = render(source, root, repair_missing=True)
            self.assertTrue(any("Unsupported link" in x for x in failures))

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


    def test_subject_directories_differing_only_in_case_share_card(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            alternate = root / "Example"
            alternate.mkdir()
            (alternate / "other.pdf").write_bytes(b"fixture")
            (alternate / "extra.pdf").write_bytes(b"fixture")
            source = BASE.replace(
                "</ul>\n</section>",
                '<li><a href="Example/other.pdf" download>other</a></li>\n</ul>\n</section>',
            )
            result, issues = render(source, root)
            self.assertFalse(issues)
            self.assertIn('href="Example/extra.pdf"', result)
            self.assertEqual(result.count('<section class="materials-group"'), 1)
            self.assertEqual(render(result, root), (result, []))

    def test_new_subject_is_inserted_before_matching_grid_close(self):
        with TemporaryDirectory() as temp:
            root = self.make_root(temp)
            (root / "new-subject").mkdir()
            (root / "new-subject" / "new.pdf").write_bytes(b"fixture")
            source = BASE.replace("</div>\n\n<script>", "</div></main>\n\n<script>")
            result, issues = render(source, root)
            self.assertFalse(issues)
            self.assertIn('href="new-subject/new.pdf"', result)
            self.assertLess(result.index('href="new-subject/new.pdf"'),
                            result.index("</div></main>"))
            self.assertEqual(render(result, root), (result, []))

    def test_current_materials_index_has_no_stale_links(self):
        from scripts.sync_materials import INDEX
        _, issues = render(INDEX.read_text(encoding="utf-8"), INDEX.parent)
        self.assertFalse(issues)

if __name__ == "__main__":
    unittest.main()
