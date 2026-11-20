#!/usr/bin/env python3
"""C4-002: Check that specification is not duplicated in non-spec files."""

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


ELEMENT_KIND_KEYWORDS = {"actor", "system", "system_web", "system_mobile",
                         "component", "queue", "storage", "microservice"}


def check_spec_dedup(parsed: ParsedFile, spec_path: Path) -> list[LintIssue]:
    """Check that non-spec files don't define element kinds."""
    issues: list[LintIssue] = []
    spec_name = spec_path.name if spec_path.name else "spec.c4"

    for block in parsed.blocks:
        if block.name != "specification":
            continue

        # This file has a specification block
        has_element_kinds = False
        for li, line in enumerate(parsed.lines):
            stripped = line.strip()
            if stripped.startswith("element ") and any(
                kw in stripped for kw in ELEMENT_KIND_KEYWORDS
            ):
                has_element_kinds = True
                break

        if has_element_kinds and parsed.path != str(spec_path):
            issues.append(LintIssue(
                file=parsed.path,
                line=1,
                severity="error",
                code="C4-002",
                message=f"Specification block found — element kinds must be in {spec_name}",
                suggestion=f"Remove 'specification {{ ... }}' from this file. Element kinds belong in {spec_name}.",
                snippet="specification { ... }",
            ))

    return issues
