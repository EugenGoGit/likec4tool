#!/usr/bin/env python3
"""C4 diagram linter — checks development rules for LikeC4 diagrams."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure scripts/ is on path
sys.path.insert(0, str(Path(__file__).parent))

from parser import parse_file
from reporter import report_issues
from checks.encoding import check_encoding
from checks.spec_dedup import check_spec_dedup
from checks.element_syntax import check_element_syntax
from checks.relationship import check_relationships
from checks.dto_format import check_dto_format
from checks.markdown_style import check_markdown_style
from checks.naming import check_naming_conventions
from checks.view_syntax import check_view_syntax


CHECKS = [
    check_encoding,
    check_spec_dedup,
    check_element_syntax,
    check_relationships,
    check_dto_format,
    check_markdown_style,
    check_naming_conventions,
    check_view_syntax,
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="C4 diagram linter — checks development rules for LikeC4 diagrams"
    )
    parser.add_argument(
        "diagrams_dir",
        nargs="?",
        default="diagrams",
        help="Directory containing .c4 files (default: diagrams/)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code on warnings",
    )
    args = parser.parse_args()

    diagrams_path = Path(args.diagrams_dir)
    if not diagrams_path.is_dir():
        print(f"Error: {diagrams_path} is not a directory", file=sys.stderr)
        return 2

    c4_files = sorted(diagrams_path.glob("*.c4"))
    if not c4_files:
        print(f"No .c4 files found in {diagrams_path}")
        return 0

    # Find spec.c4
    spec_path = diagrams_path / "spec.c4"

    all_issues = []
    for c4_file in c4_files:
        parsed = parse_file(c4_file)
        if not parsed:
            continue

        for check_fn in CHECKS:
            issues = check_fn(parsed, spec_path)
            all_issues.extend(issues)

    report_issues(all_issues)

    error_count = sum(1 for i in all_issues if i.severity == "error")
    warning_count = sum(1 for i in all_issues if i.severity == "warning")

    if error_count > 0 or (args.strict and warning_count > 0):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
