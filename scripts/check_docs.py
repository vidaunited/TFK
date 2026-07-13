#!/usr/bin/env python3
"""Validate the project's markdown docs: link integrity and table shape.

Checks every README.md / docs/*.md file for:
- balanced [] and () (catches broken/truncated markdown links)
- relative links that resolve to an existing file
- markdown tables where every row has the same column count as the header

Exits non-zero if any file has issues, printing a report to stdout.
"""
import os
import re
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


def check_brackets(text):
    issues = []
    if text.count("[") != text.count("]"):
        issues.append(f"bracket mismatch: {text.count('[')} [ vs {text.count(']')} ]")
    if text.count("(") != text.count(")"):
        issues.append(f"paren mismatch: {text.count('(')} ( vs {text.count(')')} )")
    return issues


def check_links(path, text):
    issues = []
    base = os.path.dirname(path)
    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = m.group(1).strip()
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
