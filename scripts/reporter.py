#!/usr/bin/env python3
"""Console reporter for C4 linter issues."""

from __future__ import annotations

from typing import Any

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
GRAY = "\033[90m"


SEVERITY_COLORS = {
    "error": RED,
    "warning": YELLOW,
    "info": CYAN,
}


def _colorize_severity(severity: str) -> str:
    color = SEVERITY_COLORS.get(severity, RESET)
    return color + severity.upper() + RESET


def report_issues(issues: list[Any]) -> None:
    """Print all issues to console."""
    if not issues:
        print(GREEN + "No issues found." + RESET)
        return

    by_file: dict[str, list[Any]] = {}
    for issue in issues:
        by_file.setdefault(issue.file, []).append(issue)

    for filepath, file_issues in by_file.items():
        for issue in sorted(file_issues, key=lambda i: (i.line, i.code)):
            sev = _colorize_severity(issue.severity)
            code = BOLD + issue.code + RESET
            print("\n" + code + "  " + sev + "  " + GRAY + filepath + ":" + str(issue.line) + RESET)
            print("  " + issue.message)
            if issue.suggestion:
                print("  " + GREEN + "-> " + issue.suggestion + RESET)

    error_count = sum(1 for i in issues if i.severity == "error")
    warning_count = sum(1 for i in issues if i.severity == "warning")
    info_count = sum(1 for i in issues if i.severity == "info")

    print("\n" + GRAY + ("-" * 60) + RESET)
    parts = []
    if error_count:
        label = "error" if error_count == 1 else "errors"
        parts.append(RED + str(error_count) + " " + label + RESET)
    if warning_count:
        label = "warning" if warning_count == 1 else "warnings"
        parts.append(YELLOW + str(warning_count) + " " + label + RESET)
    if info_count:
        parts.append(CYAN + str(info_count) + " info" + RESET)
    print("Found " + ", ".join(parts))
