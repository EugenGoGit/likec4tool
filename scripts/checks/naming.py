#!/usr/bin/env python3
"""C4-007: Check naming conventions for external systems."""

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

# Generic names that should be more descriptive
GENERIC_NAMES = {
    "cdn", "oauth", "ad_system", "email_service", "stripe",
    "yandex_money", "moderation_api",
}


def check_naming_conventions(parsed: ParsedFile, _spec_path: Path) -> list[LintIssue]:
    """Check naming conventions for external system elements."""
    issues: list[LintIssue] = []

    for el in parsed.all_elements:
        if el.kind == "system" and el.name in GENERIC_NAMES:
            issues.append(LintIssue(
                file=parsed.path,
                line=el.line,
                severity="warning",
                code="C4-007",
                message=f"Generic system name '{el.name}'",
                suggestion=f"Use a more descriptive name (e.g., '{el.name}_service' or '{el.name}_platform')",
                snippet=parsed.lines[el.line - 1].rstrip()[:120] if el.line else "",
            ))

    return issues
