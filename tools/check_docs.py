#!/usr/bin/env python3
"""
check_docs.py: Check every Markdown file in this repo for broken internal
links and leftover [placeholders] before anything is published.

Why: a runbook with a dead link or an unfilled placeholder looks careless,
and users stop trusting documentation that is visibly wrong.

Usage:
  python3 tools/check_docs.py            # report broken links (exit 1) and placeholders (warning)
  python3 tools/check_docs.py --strict   # placeholders also fail (use before publishing)
  python3 tools/check_docs.py path/to/docs

What it checks:
  - Relative links such as [text](runbooks/wifi-not-working.md) point to a file that exists.
  - Links with a heading anchor such as [text](#when-to-contact-it) match a real heading.
  - Bracketed placeholder text that is not a link or a checkbox.
External http(s) links are not checked, so it runs without a network connection.
Uses only the Python standard library.
"""

import argparse
import os
import re
import sys

# Bracketed text meant to stay in the published docs, because the reader fills it in.
ALLOWED_PLACEHOLDERS = {"service name", "room or area"}

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
# [text] not followed by "(" (a link) or ":" (a reference definition).
PLACEHOLDER = re.compile(r"\[([^\]]+)\](?![(:])")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
CHECKBOX = re.compile(r"^[ xX]$")


def strip_code(text):
    """
    Blank out fenced code blocks and inline code, so examples are not checked.
    Newlines are kept so reported line numbers still match the file.
    """
    text = re.sub(r"^```.*?^```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", "", text)


def slugify(heading):
    """Turn a heading into the anchor GitHub generates for it."""
    heading = re.sub(r"[*_`]", "", heading.strip().lower())
    heading = re.sub(r"[^\w\- ]", "", heading)  # drop punctuation except hyphens
    return heading.replace(" ", "-")


def headings_in(path):
    with open(path, encoding="utf-8") as handle:
        text = strip_code(handle.read())
    return {slugify(m.group(1)) for line in text.splitlines() if (m := HEADING.match(line))}


def check_file(path):
    """Return (broken_links, placeholders) for one Markdown file, each a list of (line, message)."""
    with open(path, encoding="utf-8") as handle:
        lines = strip_code(handle.read()).splitlines()

    broken, placeholders = [], []
    for number, line in enumerate(lines, start=1):
        for text, target in LINK.findall(line):
            if re.match(r"^[a-z]+:", target):  # http:, https:, mailto:
                continue
            file_part, _, anchor = target.partition("#")
            target_path = os.path.normpath(os.path.join(os.path.dirname(path), file_part)) if file_part else path
            if not os.path.exists(target_path):
                broken.append((number, f"link to '{target}' points to a file that does not exist"))
            elif anchor and target_path.endswith(".md") and anchor not in headings_in(target_path):
                broken.append((number, f"link to '{target}' has no matching heading"))

        for match in PLACEHOLDER.finditer(line):
            value = match.group(1)
            if CHECKBOX.match(value) or value.lower() in ALLOWED_PLACEHOLDERS:
                continue
            placeholders.append((number, f"placeholder [{value}]"))

    return broken, placeholders


def markdown_files(root):
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # skip .git and similar
        for name in sorted(files):
            if name.endswith(".md"):
                yield os.path.join(folder, name)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check Markdown links and placeholders.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--strict", action="store_true", help="fail on placeholders too")
    args = parser.parse_args(argv)

    total_broken = total_placeholders = 0
    for path in markdown_files(args.root):
        broken, placeholders = check_file(path)
        shown = os.path.relpath(path, args.root)
        for number, message in broken:
            print(f"BROKEN  {shown}:{number}: {message}")
        for number, message in placeholders:
            print(f"TODO    {shown}:{number}: {message}")
        total_broken += len(broken)
        total_placeholders += len(placeholders)

    print(f"\n{total_broken} broken link(s), {total_placeholders} placeholder(s).")
    if total_broken or (args.strict and total_placeholders):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
