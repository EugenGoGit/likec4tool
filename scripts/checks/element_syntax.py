#!/usr/bin/env python3
"""C4-005: Check element syntax consistency."""

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


def check_element_syntax(parsed: ParsedFile, _spec_path: Path) -> list[LintIssue]:
    """Check for mixed/incomplete element syntax."""
    issues: list[LintIssue] = []

    for el in parsed.all_elements:
        if el.is_mixed_syntax:
            issues.append(LintIssue(
                file=parsed.path,
                line=el.line,
                severity="error",
                code="C4-005a",
                message="Mixed element syntax: {} = {} '{}' {{".format(el.name, el.kind, el.title),
                suggestion="Use block form: {} = {{ title '{}'; ... }}".format(el.name, el.title),
                snippet=parsed.lines[el.line - 1].rstrip()[:120] if el.line else "",
            ))

    for i, el in enumerate(parsed.all_elements):
        if el.block_start and not el.block_end:
            if i + 1 < len(parsed.all_elements):
                next_el = parsed.all_elements[i + 1]
                if next_el.block_start and next_el.block_start < el.block_start:
                    issues.append(LintIssue(
                        file=parsed.path,
                        line=el.line,
                        severity="error",
                        code="C4-005b",
                        message="Incomplete block for element '{}' - missing closing brace".format(el.name),
                        suggestion="Add closing '}' to complete the element block.",
                        snippet=parsed.lines[el.line - 1].rstrip()[:120] if el.line else "",
                    ))

    return issues
