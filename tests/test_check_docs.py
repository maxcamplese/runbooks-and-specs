"""Tests for tools/check_docs.py. Run with: python3 -m unittest discover tests"""

import contextlib
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import check_docs as cd  # noqa: E402


class SlugifyTests(unittest.TestCase):
    def test_github_style_anchor(self):
        self.assertEqual(cd.slugify("When to contact IT"), "when-to-contact-it")

    def test_punctuation_removed_hyphens_kept(self):
        self.assertEqual(cd.slugify("Step 1: Is it just you?"), "step-1-is-it-just-you")
        self.assertEqual(cd.slugify("Wi-Fi is not working"), "wi-fi-is-not-working")


class StripCodeTests(unittest.TestCase):
    def test_keeps_line_count(self):
        text = "a\n```\n[x]\n[y]\n```\nb\n"
        self.assertEqual(cd.strip_code(text).count("\n"), text.count("\n"))
        self.assertNotIn("[y]", cd.strip_code(text))

    def test_inline_code_removed(self):
        self.assertEqual(cd.strip_code("run `ls [dir]` now"), "run  now")


class CheckFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.write("other.md", "# Real heading\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_good_links_pass(self):
        path = self.write("doc.md", "# Top\n[a](other.md) [b](other.md#real-heading) [c](#top) [d](https://x.org/[y])\n")
        broken, _ = cd.check_file(path)
        self.assertEqual(broken, [])

    def test_missing_file(self):
        path = self.write("doc.md", "[a](missing.md)\n")
        broken, _ = cd.check_file(path)
        self.assertEqual(len(broken), 1)
        self.assertIn("does not exist", broken[0][1])

    def test_missing_anchor(self):
        path = self.write("doc.md", "[a](other.md#nope)\n")
        broken, _ = cd.check_file(path)
        self.assertIn("no matching heading", broken[0][1])

    def test_placeholders_found_with_line_numbers(self):
        path = self.write("doc.md", "line one\nby [Author]\n- [ ] task\n- [x] done\n")
        _, placeholders = cd.check_file(path)
        self.assertEqual(placeholders, [(2, "placeholder [Author]")])

    def test_allowed_placeholders_ignored(self):
        path = self.write("doc.md", "Search for [service name] status.\n")
        self.assertEqual(cd.check_file(path)[1], [])

    def test_placeholder_inside_url_is_found(self):
        path = self.write("doc.md", "[repo](https://github.com/[owner]/repo)\n")
        self.assertEqual(cd.check_file(path)[1], [(1, "placeholder [owner]")])

    def test_strict_mode_fails_on_placeholders(self):
        self.write("doc.md", "by [Author]\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cd.main([self.dir]), 0)
            self.assertEqual(cd.main([self.dir, "--strict"]), 1)


if __name__ == "__main__":
    unittest.main()
