#!/usr/bin/env python3
"""Unit tests for C4 linter."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from parser import parse_file
from checks.encoding import check_encoding
from checks.spec_dedup import check_spec_dedup
from checks.element_syntax import check_element_syntax
from checks.relationship import check_relationships
from checks.dto_format import check_dto_format


FIXTURES = Path(__file__).parent / "fixtures"
DIAGRAMS = Path(__file__).parent.parent.parent / "diagrams"


class TestGoodFile(unittest.TestCase):
    """A well-formed file should produce no issues."""

    def test_no_encoding_issues(self):
        parsed = parse_file(FIXTURES / "good.c4")
        issues = check_encoding(parsed, DIAGRAMS / "spec.c4")
        self.assertEqual(len(issues), 0)

    def test_no_spec_duplication(self):
        parsed = parse_file(FIXTURES / "good.c4")
        issues = check_spec_dedup(parsed, DIAGRAMS / "spec.c4")
        self.assertEqual(len(issues), 0)

    def test_no_element_syntax_issues(self):
        parsed = parse_file(FIXTURES / "good.c4")
        issues = check_element_syntax(parsed, DIAGRAMS / "spec.c4")
        self.assertEqual(len(issues), 0)

    def test_no_short_relationships(self):
        parsed = parse_file(FIXTURES / "good.c4")
        issues = check_relationships(parsed, DIAGRAMS / "spec.c4")
        short_issues = [i for i in issues if i.code == "C4-003a"]
        self.assertEqual(len(short_issues), 0)

    def test_all_relationships_have_description(self):
        parsed = parse_file(FIXTURES / "good.c4")
        issues = check_relationships(parsed, DIAGRAMS / "spec.c4")
        desc_issues = [i for i in issues if i.code == "C4-003d"]
        self.assertEqual(len(desc_issues), 0)


class TestShortRelationship(unittest.TestCase):
    """Short form relationships should be detected."""

    def test_short_relationship_detected(self):
        parsed = parse_file(FIXTURES / "short-rel.c4")
        issues = check_relationships(parsed, DIAGRAMS / "spec.c4")
        short_issues = [i for i in issues if i.code == "C4-003a"]
        self.assertGreater(len(short_issues), 0)

    def test_missing_description_detected(self):
        parsed = parse_file(FIXTURES / "short-rel.c4")
        issues = check_relationships(parsed, DIAGRAMS / "spec.c4")
        desc_issues = [i for i in issues if i.code == "C4-003d"]
        self.assertGreater(len(desc_issues), 0)


class TestBadDTO(unittest.TestCase):
    """Malformed DTOs should be detected."""

    def test_bad_dto_detected(self):
        parsed = parse_file(FIXTURES / "bad-dto.c4")
        issues = check_dto_format(parsed, DIAGRAMS / "spec.c4")
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0].code, "C4-004")


class TestRealFiles(unittest.TestCase):
    """Test against real diagram files."""

    def test_instagram_has_no_encoding_errors(self):
        """After fix, instagram should have no encoding issues."""
        parsed = parse_file(DIAGRAMS / "instagram-service.c4")
        issues = check_encoding(parsed, DIAGRAMS / "spec.c4")
        # Should be 0 since we fixed the encoding
        self.assertEqual(len(issues), 0, f"Found encoding issues: {[i.message for i in issues]}")


if __name__ == "__main__":
    unittest.main()
