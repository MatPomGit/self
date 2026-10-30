"""Regression tests for standalone WiRR lecture slots and Bash downloads."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")


class WiRRAssetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = json.loads((ROOT / "assets/library.json").read_text(encoding="utf-8"))["entries"]
        cls.by_id = {(e["type"], e["id"]): e for e in cls.entries}

    def test_seven_lecture_pairs_have_reserved_routes(self):
        for n in range(1, 8):
            ident = str(n + 9)
            with self.subTest(lecture=n):
                pdf = self.by_id[("p", ident)]
                html = self.by_id[("h", ident)]
                self.assertIn(pdf["status"], ("planned", "ready"))
                self.assertIn(html["status"], ("draft", "ready"))
                self.assertEqual(pdf["category"], "WiRR")
                self.assertEqual(html["category"], "WiRR")
                self.assertEqual(pdf["source"], f"materials/wirr/w{n:02}.pdf")
                if pdf["status"] == "ready":
                    self.assertTrue((ROOT / pdf["source"]).is_file())
                self.assertEqual(html["source"], f"materials/wirr/lectures/w{n:02}.html")
                self.assertTrue((ROOT / html["source"]).is_file())
                self.assertTrue((ROOT / "p" / ident / "index.html").is_file())
                self.assertTrue((ROOT / "h" / ident / "index.html").is_file())

    def test_downloadable_bash_files_are_local(self):
        for ident, basename in (("02", "bash-vid.sh"), ("03", "bash-game.sh"), ("04", "bash-rpg")):
            with self.subTest(basename=basename):
                entry = self.by_id[("f", ident)]
                self.assertEqual(entry["source"], f"materials/bash/{basename}")
                self.assertEqual(entry["status"], "ready")
                self.assertTrue((ROOT / entry["source"]).is_file())
                self.assertTrue((ROOT / "f" / ident / "index.html").is_file())

    def test_wirr_landing_only_uses_local_resources(self):
        html = (ROOT / "materials/wirr/index.html").read_text(encoding="utf-8")
        self.assertNotIn("github.com/", html)
        self.assertNotRegex(html, r'href="https?://')
        self.assertEqual(len(re.findall(r'<th scope="row">Wykład ', html)), 7)
        for file in ("bash-vid.sh", "bash-game.sh", "bash-rpg"):
            self.assertIn(f'download="{file}"', html)

    @unittest.skipUnless(BASH, "Bash not installed")
    def test_script_syntax_and_help(self):
        for file in ("bash-vid.sh", "bash-game.sh", "bash-rpg"):
            path = ROOT / "materials/bash" / file
            with self.subTest(file=file):
                syntax = subprocess.run([BASH, "-n", str(path)], capture_output=True, text=True, timeout=5)
                self.assertEqual(syntax.returncode, 0, syntax.stderr)
                help_result = subprocess.run([BASH, str(path), "--help"], capture_output=True, text=True, timeout=5)
                self.assertEqual(help_result.returncode, 0, help_result.stderr)

    @unittest.skipUnless(BASH, "Bash not installed")
    def test_noninteractive_execution(self):
        work = ROOT / "materials/bash"
        commands = (
            (["bash-vid.sh", "--fast"], "", "Koniec pokazu"),
            (["bash-game.sh"], "", "koniec wejścia"),
            (["bash-rpg"], "błędna\nbłędna\nbłędna\n", "Koniec wyprawy"),
        )
        for argv, stdin, expected in commands:
            with self.subTest(script=argv[0]):
                result = subprocess.run([BASH, str(work / argv[0]), *argv[1:]], input=stdin,
                                        capture_output=True, text=True, timeout=6)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, result.stdout)


if __name__ == "__main__":
    unittest.main()
