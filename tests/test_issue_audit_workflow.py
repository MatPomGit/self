"""Issue #138: explicit, authorized on-demand audit and aggregate results."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.issue_audit_issue138 import select_scope, scopes_for, summary

ROOT = Path(__file__).resolve().parents[1]


class Issue138AuditTests(unittest.TestCase):
    def test_scope_selected_only_from_whitelisted_commands(self):
        for command, expected in (
            ("/audit", "active"),
            ("/audit active", "active"),
            ("/audit archive", "archive"),
            ("/audit both", "both"),
        ):
            self.assertEqual(select_scope("issue_comment", "", command), expected)
        self.assertEqual(select_scope("workflow_dispatch", "both", ""), "both")
        for command in ("/audit; echo unsafe", "/audit active\nunsafe", "/audit all",
                        "hello", "/audit archive "):
            with self.subTest(command=command):
                with self.assertRaises(ValueError):
                    select_scope("issue_comment", "", command)
        with self.assertRaises(ValueError):
            select_scope("workflow_dispatch", "../files", "")
        with self.assertRaises(ValueError):
            select_scope("pull_request", "both", "/audit")

    def test_scope_expansion(self):
        self.assertEqual(scopes_for("active"), ("active",))
        self.assertEqual(scopes_for("archive"), ("archive",))
        self.assertEqual(scopes_for("both"), ("active", "archive"))
        with self.assertRaises(ValueError):
            scopes_for("../../")

    def test_summary_contains_only_aggregate_counts(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for scope in ("active", "archive"):
                folder = root / scope
                folder.mkdir()
                (folder / "manifest.json").write_text(
                    json.dumps({
                        "counts": {
                            "files": 1, "logical_documents": 1, "extracted": 1,
                            "extraction_incomplete": 0, "pairs_flagged": 0
                        },
                        "sources": [{
                            "path": "SENSITIVE_SOURCE_TEXT.pdf",
                            "sha256": "a" * 64
                        }]
                    }), encoding="utf-8")
            actions, issue = summary(root, "both", "MatPomGit/self", "987654")
            for result in (actions, issue):
                self.assertIn("https://github.com/MatPomGit/self/actions/runs/987654", result)
                self.assertIn("active", result)
                self.assertIn("archive", result)
                self.assertIn("matrix.csv", result)
                self.assertNotIn("SENSITIVE_SOURCE_TEXT", result)
                self.assertIn("niezweryfikowane semantycznie", result)
            with self.assertRaises(ValueError):
                summary(root, "both", "../invalid", "123")
            with self.assertRaises(ValueError):
                summary(root, "both", "MatPomGit/self", "not-a-number")
            data = json.loads((root / "active/manifest.json").read_text())
            data["counts"]["files"] = 3
            (root / "active/manifest.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "mismatch"):
                summary(root, "active", "MatPomGit/self", "123")

    def test_untrusted_comments_only_restore_trusted_push_cache(self):
        issue = (ROOT / '.github/workflows/issue-138-audit.yml').read_text(
            encoding='utf-8')
        warm = (ROOT / '.github/workflows/issue-138-cache-warm.yml').read_text(
            encoding='utf-8')
        self.assertIn('uses: actions/cache/restore@v5', issue)
        self.assertNotIn('uses: actions/cache@v5', issue)
        self.assertIn('issue_comment:', issue)
        self.assertIn('uses: actions/cache@v5', warm)
        self.assertNotIn('issue_comment:', warm)
        self.assertIn('push:', warm)
        self.assertIn('branches: [main]', warm)
        self.assertIn('workflow_dispatch:', warm)
        self.assertIn("github.ref == 'refs/heads/main'", warm)
        self.assertIn('persist-credentials: false', warm)
        self.assertNotIn('issues: write', warm)
        self.assertNotIn('deploy-pages', warm)
        self.assertNotIn('github.event.pull_request.head', warm)
        key = 'issue138-extraction-v1-${{ runner.os }}-${{ github.sha }}-both'
        self.assertIn(key, issue)
        self.assertIn(key, warm)

    def test_workflow_prevents_untrusted_comment_execution(self):
        workflow = (ROOT / ".github/workflows/issue-138-audit.yml").read_text(
            encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("issue_comment:", workflow)
        self.assertIn("github.event.issue.number == 138", workflow)
        self.assertIn("github.event.comment.user.login == 'MatPomGit'", workflow)
        self.assertIn("github.event.comment.body == '/audit both'", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("issues: write", workflow)
        self.assertIn("issue-138-content-audit", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertNotIn("git push", workflow)
        self.assertNotIn("deploy-pages", workflow)


if __name__ == "__main__":
    unittest.main()
