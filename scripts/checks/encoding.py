#!/usr/bin/env python3
"""C4-001: Check for double-encoded UTF-8 (UTF-8 → Windows-1251 → UTF-8)."""

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


# Known double-encoding artifacts (UTF-8 bytes re-interpreted as Windows-1251)
KNOWN_PATTERNS = [
    # Common punctuation
    ("\u0420\u0412\u0422\u041c", "\u2014", "em-dash (—)"),
    ("\u0420\u0411\u0422\u041c", "\u2013", "en-dash (–)"),
    ("\u0420\u0412\u0422\u0410", "\u201c", "left double quote (\u201c)"),
    ("\u0420\u0412\u0422\u041a", "\u201d", "right double quote (\u201d)"),
    ("\u0420\u0412\u0422\u0418", "\u2018", "left single quote (\u2018)"),
    ("\u0420\u0412\u0422\u041a", "\u2019", "right single quote (\u2019)"),
    ("\u0420\u0412\u0422\u0410", "\u2026", "ellipsis (\u2026)"),
    ("\u0420\u0422\u0410", "\u2122", "trademark (\u2122)"),
    ("\u0420\u0422\u0410", "\u00ae", "registered (\u00ae)"),
    ("\u0420\u0422\u0410", "\u00a9", "copyright (\u00a9)"),
    ("\u0420\u0412\u0422\u0410", "\u2022", "bullet (\u2022)"),
    ("\u0420\u0412\u0422\u0410", "\u00a7", "section (\u00a7)"),
    ("\u0420\u0412\u0422\u0410", "\u00b6", "paragraph (\u00b6)"),
    ("\u0420\u0412\u0422\u0410", "\u00b0", "degree (\u00b0)"),
    ("\u0420\u0412\u0422\u0410", "\u00b1", "plus-minus (\u00b1)"),
]


def check_encoding(parsed: ParsedFile, _spec_path: Path) -> list[LintIssue]:
    """Check for double-encoded UTF-8 in file content."""
    text = parsed.raw_bytes.decode("utf-8", errors="replace")
    issues: list[LintIssue] = []

    for line_idx, line in enumerate(parsed.lines):
        line_num = line_idx + 1
        for pattern, replacement, name in KNOWN_PATTERNS:
            if pattern in line:
                issues.append(LintIssue(
                    file=parsed.path,
                    line=line_num,
                    severity="error",
                    code="C4-001",
                    message=f"Double-encoded UTF-8 detected (should be {name})",
                    suggestion=f"Replace {pattern!r} with {replacement!r} ({name})",
                    snippet=line.rstrip()[:120],
                ))

    return issues
