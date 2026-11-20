#!/usr/bin/env python3
"""Fix notes/description in C4 files according to AGENT.md rules."""

import re
from pathlib import Path


def fix_file(filepath: str) -> None:
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")
    
    # Split into model and views sections
    views_marker = "\nviews {"
    views_idx = content.find(views_marker)
    
    if views_idx == -1:
        print(f"  No views section found in {filepath}")
        return
    
    model_section = content[:views_idx]
    views_section = content[views_idx:]
    
    # Fix model section: replace '    notes ' with '    description '
    # Model relationships use 4-space indent for properties
    model_section = re.sub(r'^(\s+)notes\s', r'\1description ', model_section, flags=re.MULTILINE)
    
    # Fix views section: in dynamic views, replace 'description' with 'notes'
    views_section = _fix_dynamic_views(views_section)
    
    result = model_section + views_section
    path.write_text(result, encoding="utf-8")
    print(f"  Fixed: {filepath}")


def _fix_dynamic_views(text: str) -> str:
    """In dynamic view blocks, replace 'description' with 'notes'."""
    lines = text.split('\n')
    result = []
    in_dynamic_view = False
    brace_depth = 0
    
    for line in lines:
        if re.match(r'\s*dynamic view\s+', line):
            in_dynamic_view = True
            brace_depth = line.count('{') - line.count('}')
            result.append(line)
            continue
        
        if in_dynamic_view:
            brace_depth += line.count('{') - line.count('}')
            
            # Replace '      description ' with '      notes ' (6-space indent)
            match = re.match(r'^(\s{6,})description\s', line)
            if match:
                line = match.group(1) + "notes " + line[match.end(0) - len(match.group(0)):].lstrip()
                # Actually just replace the word
                line = re.sub(r'^(\s{6,})description\s', r'\1notes ', line)
            
            if brace_depth <= 0:
                in_dynamic_view = False
                brace_depth = 0
        
        result.append(line)
    
    return '\n'.join(result)


if __name__ == "__main__":
    import sys
    files = sys.argv[1:]
    if not files:
        print("Usage: python fix_notes_description.py <file1.c4> [file2.c4 ...]")
        sys.exit(1)
    
    for f in files:
        fix_file(f)
