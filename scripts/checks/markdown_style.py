#!/usr/bin/env python3
"""C4-006: Check markdown style in descriptions and notes."""

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


SECTION_HEADER_RE = re.compile(r"^#{2,}\s+\w")


def check_markdown_style(parsed: ParsedFile, _spec_path: Path) -> list[LintIssue]:
    """Check that descriptions and notes use ### section headers."""
    issues: list[LintIssue] = []

    for rel in parsed.all_relationships:
        for text_field, field_name in [
            (rel.description, "description"),
            (rel.notes, "notes"),
        ]:
            if not text_field:
                continue

            lines = text_field.strip().split("\n")
            has_section = any(
                SECTION_HEADER_RE.match(l.strip()) for l in lines if l.strip()
            )

            # Check if content is just a single plain sentence
            non_empty = [l.strip() for l in lines if l.strip()]
            if len(non_empty) <= 2 and not has_section:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=rel.line,
                    severity="warning",
                    code="C4-006",
                    message=f"{field_name} lacks ### section headers",
                    suggestion="Organize content with ### headers (e.g., ### REST API Endpoints, ### DTO)",
                    snippet=text_field[:120],
                ))

    return issues
