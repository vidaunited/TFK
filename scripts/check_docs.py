#!/usr/bin/env python3
"""Validate the project's markdown docs: link integrity and table shape.

Checks every README.md / docs/*.md file for:
- well-formed markdown link syntax: every `[text](` opener closes on the
  same line (catches broken/truncated links without tripping on ordinary
  brackets or parentheses in prose)
- relative links that resolve to an existing file
- markdown tables where every row has the same column count as the header

Exits non-zero if any file has issues, printing a report to stdout.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_docs():
    docs = [os.path.join(ROOT, "README.md")]
    docs_dir = os.path.join(ROOT, "docs")
    if os.path.isdir(docs_dir):
        for name in sorted(os.listdir(docs_dir)):
            if name.endswith(".md"):
                docs.append(os.path.join(docs_dir, name))
    return [d for d in docs if os.path.isfile(d)]


# A markdown link is `[text](target)`; an image is `![alt](target)`. This is a
# tiny hand parser rather than a regex so that a target may contain one level
# of nested parentheses (`[w](https://en.wikipedia.org/wiki/Foo_(bar))`), and so
# that a truncated link (`[text](docs/a.md` with no closing paren) is reported
# without counting every `[` and `(` in the prose around it.
def parse_links(text):
    """Return (links, issues).

    links  -- list of (text, target, line_number) for every well-formed link
    issues -- list of strings for `[text](` openers whose target never closes
              on the same line (a broken or truncated link)
    """
    links = []
    issues = []
    line_no = 1
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\n":
            line_no += 1
            i += 1
            continue
        if ch != "[":
            i += 1
            continue
        # Link text: up to the matching `]` on this line, allowing nested `[]`.
        depth = 1
        j = i + 1
        while j < n and text[j] != "\n" and depth > 0:
            if text[j] == "[":
                depth += 1
            elif text[j] == "]":
                depth -= 1
            j += 1
        if depth != 0 or j >= n or text[j] != "(":
            # `[...` that is not followed by `(` is prose or a reference-style
            # link, not an inline link — nothing to check.
            i += 1
            continue
        link_text = text[i + 1 : j - 1]
        # Target: up to the matching `)` on this line, allowing nested `()`.
        depth = 1
        k = j + 1
        while k < n and text[k] != "\n" and depth > 0:
            if text[k] == "(":
                depth += 1
            elif text[k] == ")":
                depth -= 1
            k += 1
        if depth != 0:
            snippet = text[i:j + 1]
            issues.append(f"unterminated link at line {line_no}: {snippet}...")
            i = j + 1
            continue
        links.append((link_text, text[j + 1 : k - 1], line_no))
        i = k
    return links, issues


def check_brackets(text):
    """Report `[text](` openers that never close — the truncated-link case."""
    return parse_links(text)[1]


def check_links(path, text):
    issues = []
    base = os.path.dirname(path)
    for _text, raw_target, _line in parse_links(text)[0]:
        target = raw_target.strip()
        # `[text](target "title")` — drop the optional title.
        if " " in target and target.split(" ", 1)[1].lstrip().startswith(('"', "'")):
            target = target.split(" ", 1)[0]
        if target.startswith("http://") or target.startswith("https://") or target.startswith("#") or target.startswith("mailto:"):
            continue
        target_path = target.split("#", 1)[0]
        resolved = os.path.normpath(os.path.join(base, target_path))
        if not os.path.exists(resolved):
            issues.append(f"broken link: {target} -> {os.path.relpath(resolved, ROOT)}")
    return issues


def check_tables(text):
    issues = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|"):
            header_cols = line.count("|")
            block_start = i
            j = i + 1
            row_num = 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                cols = lines[j].count("|")
                if cols != header_cols:
                    issues.append(
                        f"table column mismatch at line {j + 1} (row {row_num} of block starting line {block_start + 1}): "
                        f"expected {header_cols} pipes, got {cols}"
                    )
                row_num += 1
                j += 1
            i = j
        else:
            i += 1
    return issues


def main():
    docs = find_docs()
    if not docs:
        print("No markdown docs found.")
        return 0

    had_issues = False
    for path in docs:
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding="utf-8").read()
        issues = check_brackets(text) + check_links(path, text) + check_tables(text)
        if issues:
            had_issues = True
            print(f"FAIL {rel}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"OK   {rel}")

    return 1 if had_issues else 0


if __name__ == "__main__":
    sys.exit(main())
