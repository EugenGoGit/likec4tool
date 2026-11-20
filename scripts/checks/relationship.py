#!/usr/bin/env python3
"""C4-003: Check relationship completeness and syntax."""

from __future__ import annotations

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


def check_relationships(parsed: ParsedFile, _spec_path: Path) -> list[LintIssue]:
    """Check that relationships use block syntax with required fields."""
    issues: list[LintIssue] = []

    for rel in parsed.all_relationships:
        # C4-003a: Short form relationship
        if rel.is_short_form:
            # Dynamic view short relationships are warnings, not errors
            severity = "warning" if rel.is_dynamic_view else "error"
            issues.append(LintIssue(
                file=parsed.path,
                line=rel.line,
                severity=severity,
                code="C4-003a",
                message=f"Short relationship syntax: '{rel.source} -> {rel.target} {rel.label}'",
                suggestion="Use block form with title, technology, and description fields.",
                snippet=parsed.lines[rel.line - 1].rstrip()[:120] if rel.line else "",
            ))
            continue

        # C4-003b: Missing title
        if not rel.title:
            issues.append(LintIssue(
                file=parsed.path,
                line=rel.line,
                severity="error",
                code="C4-003b",
                message=f"Relationship missing 'title': '{rel.source} -> {rel.target}'",
                suggestion="Add title field: title 'description of relationship'",
                snippet=parsed.lines[rel.line - 1].rstrip()[:120] if rel.line else "",
            ))

        # C4-003c: Missing technology
        if not rel.technology:
            issues.append(LintIssue(
                file=parsed.path,
                line=rel.line,
                severity="error",
                code="C4-003c",
                message=f"Relationship missing 'technology': '{rel.source} -> {rel.target}'",
                suggestion="Add technology field: technology 'protocol/tech'",
                snippet=parsed.lines[rel.line - 1].rstrip()[:120] if rel.line else "",
            ))

        # C4-003d: Missing description (static) or notes (dynamic)
        if rel.is_dynamic_view:
            if not rel.notes:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=rel.line,
                    severity="error",
                    code="C4-003d",
                    message=f"Dynamic view relationship missing 'notes': '{rel.source} -> {rel.target}'",
                    suggestion="Add notes with ### DTO section for dynamic view relationships",
                    snippet=parsed.lines[rel.line - 1].rstrip()[:120] if rel.line else "",
                ))
        else:
            if not rel.description:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=rel.line,
                    severity="error",
                    code="C4-003d",
                    message=f"Relationship missing 'description': '{rel.source} -> {rel.target}'",
                    suggestion="Add description with ### DTO section",
                    snippet=parsed.lines[rel.line - 1].rstrip()[:120] if rel.line else "",
                ))

    return issues
