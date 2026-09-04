"""Unit tests for scripts/check_docs.py.

Run with:  python3 -m unittest scripts/test_check_docs.py
"""
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_docs  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LinkSyntaxTests(unittest.TestCase):
    def test_unbalanced_paren_in_prose_passes(self):
        text = "Retail prices (a\nare set per branch. See [b] and (c] too.\n"
        self.assertEqual(check_docs.check_brackets(text), [])

    def test_unbalanced_bracket_in_prose_passes(self):
        self.assertEqual(check_docs.check_brackets("Sizes [S, M, L are stocked.\n"), [])

    def test_truncated_link_fails(self):
        issues = check_docs.check_brackets("See [the guide](docs/guide.md for details.\n")
        self.assertEqual(len(issues), 1)
        self.assertIn("unterminated link at line 1", issues[0])

    def test_truncated_link_reports_correct_line(self):
        issues = check_docs.check_brackets("intro\n\nSee [x](docs/x.md\n")
        self.assertEqual(len(issues), 1)
        self.assertIn("line 3", issues[0])

    def test_reference_style_link_is_not_flagged(self):
        self.assertEqual(check_docs.check_brackets("See [the guide][guide].\n"), [])


class ParseLinksTests(unittest.TestCase):
    def test_target_with_nested_parentheses_parses_whole_target(self):
        links, issues = check_docs.parse_links("[w](https://en.wikipedia.org/wiki/Foo_(bar)) tail\n")
        self.assertEqual(issues, [])
        self.assertEqual(links, [("w", "https://en.wikipedia.org/wiki/Foo_(bar)", 1)])

    def test_image_and_multiple_links_on_one_line(self):
        links, issues = check_docs.parse_links("![logo](img/logo.png) and [a](x.md) and [b](y.md#s)\n")
        self.assertEqual(issues, [])
        self.assertEqual([t for _, t, _ in links], ["img/logo.png", "x.md", "y.md#s"])

    def test_link_text_with_nested_brackets(self):
        links, issues = check_docs.parse_links("[see [note]](docs/n.md)\n")
        self.assertEqual(issues, [])
        self.assertEqual(links, [("see [note]", "docs/n.md", 1)])


class CheckLinksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "docs"))
        with open(os.path.join(self.root, "docs", "exists.md"), "w") as f:
            f.write("# ok\n")
        with open(os.path.join(self.root, "docs", "a_(b).md"), "w") as f:
            f.write("# ok\n")
        self.readme = os.path.join(self.root, "README.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_broken_relative_link_fails(self):
        issues = check_docs.check_links(self.readme, "See [x](docs/missing.md).\n")
        self.assertEqual(len(issues), 1)
        self.assertTrue(issues[0].startswith("broken link: docs/missing.md -> "))

    def test_existing_relative_link_passes(self):
        self.assertEqual(check_docs.check_links(self.readme, "See [x](docs/exists.md#top).\n"), [])

    def test_relative_target_containing_parenthesis_resolves(self):
        self.assertEqual(check_docs.check_links(self.readme, "See [x](docs/a_(b).md).\n"), [])

    def test_external_and_anchor_links_are_skipped(self):
        text = "[a](https://example.com/x_(y)) [b](#section) [c](mailto:x@y.z)\n"
        self.assertEqual(check_docs.check_links(self.readme, text), [])

    def test_truncated_link_is_not_treated_as_a_target(self):
        # The truncated opener is reported by check_brackets, not resolved here.
        self.assertEqual(check_docs.check_links(self.readme, "[x](docs/missing.md\n"), [])


class EndToEndTests(unittest.TestCase):
    def test_real_docs_still_pass(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "check_docs.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        self.assertTrue(lines, "no output")
        self.assertTrue(all(l.startswith("OK   ") for l in lines), proc.stdout)

    def test_output_format_on_failure(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "README.md"), "w") as f:
                f.write("Prose (a with [x](nope.md) and [y](docs/z.md\n")
            script = os.path.join(root, "check_docs.py")
            with open(os.path.join(ROOT, "scripts", "check_docs.py")) as src, open(script, "w") as dst:
                dst.write(src.read().replace(
                    "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
                    f"ROOT = {root!r}",
                ))
            proc = subprocess.run([sys.executable, script], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            out = proc.stdout.splitlines()
            self.assertEqual(out[0], "FAIL README.md")
            self.assertIn("  - unterminated link at line 1: [y](...", out)
            self.assertTrue(any(l.startswith("  - broken link: nope.md -> ") for l in out), out)


if __name__ == "__main__":
    unittest.main()
