#!/usr/bin/env python3
"""C4-004: Check DTO formatting in descriptions and notes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from parser import ParsedFile


@dataclass
class LintIssue:
    file: str
    line: int
    severity: str
    code: str
    message: str
    suggestion: str
    snippet: str


# DTO pattern: - RecordName { field1, field2, ... }
DTO_PATTERN = re.compile(r"^\s*-\s+([A-Z][a-zA-Z0-9]*)\s*\{[^}]*\}")
# Invalid DTO: missing PascalCase or braces
BAD_DTO_PATTERN = re.compile(r"^\s*-\s+(.+?)\s*$")


def _check_dto_sections(text: str, start_line: int) -> list[LintIssue]:
    """Check DTO formatting within a text block."""
    issues = []
    lines = text.split("\n")
    in_dto = False
    dto_start = start_line

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("### DTO"):
            in_dto = True
            continue

        if in_dto:
            if stripped.startswith("###"):
                in_dto = False
                continue

            # Check if this looks like a DTO entry
            if stripped.startswith("- "):
                if not DTO_PATTERN.match(stripped):
                    issues.append(LintIssue(
                        file="",  # will be set by caller
                        line=start_line + i,
                        severity="error",
                        code="C4-004",
                        message=f"Malformed DTO entry: '{stripped}'",
                        suggestion="Use format: - RecordName { field1, field2, ... }",
                        snippet=stripped[:120],
                    ))

    return issues


def check_dto_format(parsed: ParsedFile, _spec_path: Path) -> list[LintIssue]:
    """Check DTO formatting in all descriptions and notes."""
    issues: list[LintIssue] = []

    # Check relationship descriptions and notes
    for rel in parsed.all_relationships:
        if rel.description:
            rel_issues = _check_dto_sections(rel.description, rel.line)
            for iss in rel_issues:
                iss.file = parsed.path
            issues.extend(rel_issues)

        if rel.notes:
            rel_issues = _check_dto_sections(rel.notes, rel.line)
            for iss in rel_issues:
                iss.file = parsed.path
            issues.extend(rel_issues)

    return issues
