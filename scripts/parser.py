#!/usr/bin/env python3
"""
LikeC4 DSL parser — regex-based parser for .c4 files.

Returns structured representation of elements, relationships, and blocks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


ELEMENT_KINDS = {
    "actor", "system", "system_web", "system_mobile",
    "component", "queue", "storage", "microservice",
}

TOP_LEVEL_RE = re.compile(r"^\s*(dynamic view|specification|model|views|global|diff)(?:\s+([\w-]+))?\s*\{")


@dataclass
class Element:
    name: str
    kind: str
    title: Optional[str] = None
    description_text: Optional[str] = None
    technology: Optional[str] = None
    line: int = 0
    properties: dict = field(default_factory=dict)
    block_start: Optional[int] = None  # line where { was found
    block_end: Optional[int] = None    # line where } closes it
    is_mixed_syntax: bool = False      # has title in short form + block


@dataclass
class Relationship:
    source: str
    target: str
    label: Optional[str] = None
    title: Optional[str] = None
    technology: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    line: int = 0
    is_short_form: bool = False
    is_dynamic_view: bool = False
    block_start: Optional[int] = None


@dataclass
class ParsedBlock:
    name: str  # "specification", "model", "views", etc.
    start_line: int
    end_line: int
    elements: list = field(default_factory=list)
    relationships: list = field(default_factory=list)
    raw_lines: list = field(default_factory=list)


@dataclass
class ParsedFile:
    path: str
    raw_bytes: bytes = field(default_factory=bytes)
    lines: list = field(default_factory=list)
    blocks: list = field(default_factory=list)  # ParsedBlock
    spec_element_kinds: set = field(default_factory=set)
    all_elements: list = field(default_factory=list)  # Element
    all_relationships: list = field(default_factory=list)  # Relationship
    parse_errors: list = field(default_factory=list)


# Regex patterns
BLOCK_ELEMENT_RE = re.compile(r"^\s*(\w+)\s*=\s*(\w+)\s*\{")
MIXED_ELEMENT_RE = re.compile(r"^\s*(\w+)\s*=\s*(\w+)\s+'([^']+)'\s*\{")
SIMPLE_ELEMENT_RE = re.compile(r"^\s*(\w+)\s*=\s*(\w+)\s*$")
ELEMENT_WITH_TITLE_RE = re.compile(r"^\s*(\w+)\s*=\s*(\w+)\s+'([^']+)'\s*$")
ELEMENT_WITH_TITLE_AND_DESC_RE = re.compile(
    r"^\s*(\w+)\s*=\s*(\w+)\s+'([^']+)'\s+'([^']+)'\s*$"
)
SIMPLE_KIND_ELEMENT_RE = re.compile(
    r"^\s*(actor|system|system_web|system_mobile|component|queue|storage|microservice)\s+(\w+)\s*$"
)
SIMPLE_KIND_ELEMENT_COMMENT_RE = re.compile(
    r"^\s*(actor|system|system_web|system_mobile|component|queue|storage|microservice)\s+(\w+)\s+('.*?')\s*$"
)

SHORT_REL_RE = re.compile(
    r"^\s*(\w+(?:\.\w+)?)\s*->\s*(\w+(?:\.\w+)?)\s+'([^']+)'\s*$"
)
BLOCK_REL_RE = re.compile(
    r"^\s*(\w+(?:\.\w+)?)\s*->\s*(\w+(?:\.\w+)?)\s*\{"
)
BIDI_REL_RE = re.compile(
    r"^\s*(\w+(?:\.\w+)?)\s*<->\s*(\w+(?:\.\w+)?)\s*$"
)

# Pattern to match nested view blocks (view or dynamic view)
NESTED_VIEW_RE = re.compile(
    r"^\s*(dynamic view|view)\s+([\w-]+)\s*\{"
)

TITLE_PROP_RE = re.compile(r"^\s*title\s+'([^']+)'\s*$")
TECHNOLOGY_PROP_RE = re.compile(r"^\s*technology\s+'([^']+)'\s*$")
DESC_START_RE = re.compile(r"^\s*description\s+'''")
NOTES_START_RE = re.compile(r"^\s*notes\s+'''")
DESC_END_RE = re.compile(r"^\s*'''")

SPEC_ELEMENT_KIND_RE = re.compile(
    r"^\s*element\s+(\w+)(?:\s*\{)?\s*$"
)


def _read_file(path: Path) -> tuple[bytes, list[str]]:
    """Read file with fallback encodings."""
    for enc in ("utf-8", "windows-1251", "cp1252"):
        try:
            raw = path.read_bytes()
            text = raw.decode(enc)
            return raw, text.splitlines(keepends=True)
        except (UnicodeDecodeError, ValueError):
            continue
    raw = path.read_bytes()
    return raw, raw.decode("utf-8", errors="replace").splitlines(keepends=True)


def _strip_comment(line: str) -> str:
    """Remove // comments, respecting strings."""
    in_single = False
    in_triple = False
    i = 0
    while i < len(line):
        ch = line[i]
        if not in_triple and ch == "'" and (i + 2 < len(line) and line[i+1:i+3] == "''"):
            in_single = True
            i += 3
            continue
        if in_single and i + 2 < len(line) and line[i:i+3] == "'''":
            in_single = False
            i += 3
            continue
        if not in_single and ch == "/" and i + 1 < len(line) and line[i+1] == "/":
            return line[:i]
        i += 1
    return line


def _find_block_end(lines: list[str], start: int) -> int:
    """Find matching closing brace for block starting at `start`."""
    depth = 0
    in_triple = False
    for i in range(start, len(lines)):
        line = _strip_comment(lines[i])
        # Track triple-quoted strings
        if "'''" in line:
            count = line.count("'''")
            if count % 2 == 1:
                in_triple = not in_triple
            if in_triple:
                continue
        if not in_triple:
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                return i
    return len(lines) - 1


def _parse_block_content(
    lines: list[str],
    block_start_idx: int,
    block_end_idx: int,
    is_dynamic_view: bool = False,
) -> tuple[list[Element], list[Relationship]]:
    """Parse elements and relationships within a block."""
    elements: list[Element] = []
    relationships: list[Relationship] = []

    i = block_start_idx
    while i <= block_end_idx:
        line = lines[i]
        stripped = _strip_comment(line).rstrip()
        line_num = i + 1



        # Skip empty lines, comments, block openers/closers
        if not stripped or stripped in ("{", "}"):
            i += 1
            continue

        # Skip nested view blocks (view or dynamic view)
        nested_view_match = NESTED_VIEW_RE.match(stripped)
        if nested_view_match:
            # Find the matching closing brace and skip the entire block
            block_end = _find_block_end(lines, i)
            i = block_end + 1
            continue

        # Check for triple-quoted strings — skip content lines
        if "'''" in stripped:
            i += 1
            continue

        # Check for property inside a block (title, technology, etc.)
        # These are handled when we're inside an element/relationship block

        # Try to detect element definitions
        mixed_match = MIXED_ELEMENT_RE.match(stripped)
        if mixed_match:
            name, kind, title = mixed_match.groups()
            el = Element(
                name=name, kind=kind, title=title,
                line=line_num, is_mixed_syntax=True,
                block_start=line_num,
            )
            elements.append(el)
            i += 1
            continue

        block_match = BLOCK_ELEMENT_RE.match(stripped)
        if block_match:
            name, kind = block_match.groups()
            el = Element(
                name=name, kind=kind,
                line=line_num,
                block_start=line_num,
            )
            # Parse properties until }
            prop_lines = []
            j = i + 1
            while j <= block_end_idx:
                pl = _strip_comment(lines[j]).rstrip()
                if not pl or pl == "}":
                    break
                prop_lines.append((j + 1, pl))
                if DESC_START_RE.match(pl) or NOTES_START_RE.match(pl):
                    # Multi-line string — skip until closing '''
                    j += 1
                    while j <= block_end_idx:
                        if DESC_END_RE.match(_strip_comment(lines[j])):
                            break
                        j += 1
                j += 1
            el.block_end = j
            for plen, pline in prop_lines:
                tm = TITLE_PROP_RE.match(pline)
                if tm:
                    el.title = tm.group(1)
                tch = TECHNOLOGY_PROP_RE.match(pline)
                if tch:
                    el.technology = tch.group(1)
            elements.append(el)
            i += 1
            continue

        simple_match = SIMPLE_ELEMENT_RE.match(stripped)
        if simple_match:
            name, kind = simple_match.groups()
            elements.append(Element(name=name, kind=kind, line=line_num))
            i += 1
            continue

        title_match = ELEMENT_WITH_TITLE_RE.match(stripped)
        if title_match:
            name, kind, title = title_match.groups()
            elements.append(Element(name=name, kind=kind, title=title, line=line_num))
            i += 1
            continue

        title_desc_match = ELEMENT_WITH_TITLE_AND_DESC_RE.match(stripped)
        if title_desc_match:
            name, kind, title, desc = title_desc_match.groups()
            elements.append(
                Element(name=name, kind=kind, title=title,
                        description_text=desc, line=line_num)
            )
            i += 1
            continue

        kind_match = SIMPLE_KIND_ELEMENT_RE.match(stripped)
        if kind_match:
            kind, name = kind_match.groups()
            elements.append(Element(name=name, kind=kind, line=line_num))
            i += 1
            continue

        kind_comment_match = SIMPLE_KIND_ELEMENT_COMMENT_RE.match(stripped)
        if kind_comment_match:
            kind, name, _ = kind_comment_match.groups()
            elements.append(Element(name=name, kind=kind, line=line_num))
            i += 1
            continue



        # Try to detect relationships
        short_match = SHORT_REL_RE.match(stripped)
        if short_match:
            src, tgt, label = short_match.groups()
            rel = Relationship(
                source=src, target=tgt, label=label,
                line=line_num, is_short_form=True,
                is_dynamic_view=is_dynamic_view,
            )
            relationships.append(rel)
            i += 1
            continue

        block_rel_match = BLOCK_REL_RE.match(stripped)
        if block_rel_match:
            src, tgt = block_rel_match.groups()
            rel = Relationship(
                source=src, target=tgt,
                line=line_num,
                block_start=line_num,
                is_dynamic_view=is_dynamic_view,
            )
            # Parse properties until }
            j = i + 1
            while j <= block_end_idx:
                pl = _strip_comment(lines[j]).rstrip()
                if not pl or pl == "}":
                    break
                tm = TITLE_PROP_RE.match(pl)
                if tm:
                    rel.title = tm.group(1)
                tch = TECHNOLOGY_PROP_RE.match(pl)
                if tch:
                    rel.technology = tch.group(1)
                if DESC_START_RE.match(pl):
                    j += 1
                    desc_parts = []
                    while j <= block_end_idx:
                        dl = _strip_comment(lines[j]).rstrip()
                        if DESC_END_RE.match(dl):
                            break
                        desc_parts.append(dl)
                        j += 1
                    rel.description = "\n".join(desc_parts)
                    rel.block_end = j
                    j += 1
                    continue
                if NOTES_START_RE.match(pl):
                    j += 1
                    notes_parts = []
                    while j <= block_end_idx:
                        nl = _strip_comment(lines[j]).rstrip()
                        if DESC_END_RE.match(nl):
                            break
                        notes_parts.append(nl)
                        j += 1
                    rel.notes = "\n".join(notes_parts)
                    rel.block_end = j
                    j += 1
                    continue
                j += 1
            rel.block_end = j
            relationships.append(rel)
            i += 1
            continue

        bidi_match = BIDI_REL_RE.match(stripped)
        if bidi_match:
            src, tgt = bidi_match.groups()
            relationships.append(
                Relationship(source=src, target=tgt, line=line_num)
            )
            i += 1
            continue

        i += 1

    return elements, relationships


def parse_file(path: Path) -> Optional[ParsedFile]:
    """Parse a .c4 file and return a ParsedFile object."""
    raw, lines = _read_file(path)
    parsed = ParsedFile(path=str(path), raw_bytes=raw, lines=lines)

    # Find top-level blocks
    i = 0
    while i < len(lines):
        stripped = _strip_comment(lines[i]).rstrip()
        line_num = i + 1

        block_match = TOP_LEVEL_RE.match(stripped)
        if block_match:
            block_name = block_match.group(1)
            block_start = i
            block_end = _find_block_end(lines, i)

            # Extract spec element kinds
            if block_name == "specification":
                for li in range(block_start + 1, block_end):
                    sm = SPEC_ELEMENT_KIND_RE.match(_strip_comment(lines[li]))
                    if sm:
                        parsed.spec_element_kinds.add(sm.group(1))

            # Parse content
            is_dynamic = block_name == "dynamic view"
            elements, relationships = _parse_block_content(
                lines, block_start + 1, block_end - 1,
                is_dynamic_view=is_dynamic,
            )

            block = ParsedBlock(
                name=block_name,
                start_line=line_num,
                end_line=block_end + 1,
                elements=elements,
                relationships=relationships,
            )
            parsed.blocks.append(block)

            # Handle nested dynamic views inside views block
            if block_name == "views":
                j = block_start + 1
                while j < block_end:
                    dsl = _strip_comment(lines[j]).rstrip()
                    dv_match = TOP_LEVEL_RE.match(dsl)
                    if dv_match and dv_match.group(1) == "dynamic view":
                        dv_name = dv_match.group(2) or "unnamed"
                        dv_start = j
                        dv_end = _find_block_end(lines, j)
                        dv_elements, dv_rels = _parse_block_content(
                            lines, dv_start + 1, dv_end - 1,
                            is_dynamic_view=True,
                        )
                        dv_block = ParsedBlock(
                            name="dynamic view",
                            start_line=j + 1,
                            end_line=dv_end + 1,
                            elements=dv_elements,
                            relationships=dv_rels,
                        )
                        parsed.blocks.append(dv_block)
                        parsed.all_relationships.extend(dv_rels)
                        j = dv_end + 1
                    else:
                        j += 1

            if block_name == "model":
                parsed.all_elements.extend(elements)
                parsed.all_relationships.extend(relationships)
            elif "view" in block_name or "dynamic" in block_name:
                parsed.all_relationships.extend(relationships)

            i = block_end + 1
        else:
            i += 1

    return parsed
