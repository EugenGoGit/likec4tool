#!/usr/bin/env python3
"""
C4-008: Dynamic view relationships must have notes, not description.
C4-009: Static view relationships must have description, not notes.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
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


def check_view_syntax(parsed: ParsedFile, _spec_path: Path) -> list[LintIssue]:
    """Check that view relationships follow correct property rules."""
    issues: list[LintIssue] = []

    for rel in parsed.all_relationships:
        if not rel.line:
            continue

        snippet = parsed.lines[rel.line - 1].rstrip()[:120] if rel.line else ""

        if rel.is_dynamic_view:
            # C4-008: Dynamic view — must have notes, must NOT have description
            if not rel.notes:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=rel.line,
                    severity="error",
                    code="C4-008",
                    message=f"Dynamic view relationship missing 'notes': '{rel.source} -> {rel.target}'",
                    suggestion="Use 'notes' for dynamic view steps, not 'description'.",
                    snippet=snippet,
                ))
            if rel.description:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=rel.line,
                    severity="error",
                    code="C4-008",
                    message=f"Dynamic view relationship has 'description' — should use 'notes': '{rel.source} -> {rel.target}'",
                    suggestion="Replace 'description' with 'notes' in dynamic view relationships.",
                    snippet=snippet,
                ))
        else:
            # C4-009: Static view (model relationships) — must have description, must NOT have notes
            if not rel.description:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=rel.line,
                    severity="error",
                    code="C4-009",
                    message=f"Static view relationship missing 'description': '{rel.source} -> {rel.target}'",
                    suggestion="Add 'description' with ### DTO section for static view relationships.",
                    snippet=snippet,
                ))
            if rel.notes:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=rel.line,
                    severity="error",
                    code="C4-009",
                    message=f"Static view relationship has 'notes' — should use 'description': '{rel.source} -> {rel.target}'",
                    suggestion="Replace 'notes' with 'description' in static view (model) relationships.",
                    snippet=snippet,
                ))

    return issues
