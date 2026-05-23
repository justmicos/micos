#!/usr/bin/env python3
"""
absorb-osp — YAML Frontmatter Validator

Validates YAML frontmatter in template markdown files.
Checks for required fields, correct types, and valid values.
Usage:
    python scripts/validate.py <file_or_directory>
    python scripts/validate.py templates/analysis_report.md
    python scripts/validate.py templates/
"""

import os
import re
import sys
import json

# ── Required frontmatter schema per file type ──────────────────────

SCHEMAS = {
    "analysis_report.md": {
        "required": [
            ("absorb_date", str, "YYYY-MM-DD"),
            ("github_url", str, "https://github.com/owner/repo"),
            ("license", str, "MIT/Apache-2.0/GPL-3.0/Other"),
            ("depth", str, "L1/L2/L3/L4/L5"),
            ("status", str, "online/built/installed/rejected/deferred"),
            ("judge_score", (int, float), "X.X"),
            ("classify_decision", str, "MERGE/SUPERSEDE/ENHANCE/STANDALONE"),
        ],
        "optional": [
            ("stars", (int, float), "N"),
            ("integration_targets", list, "[...]"),
        ],
    },
    "usage_log.md": {
        "required": [
            ("project", str, "<project-name>"),
            ("github_url", str, "https://github.com/owner/repo"),
            ("absorb_date", str, "YYYY-MM-DD"),
            ("last_updated", str, "YYYY-MM-DD"),
        ],
    },
    "instinct.md": {
        "required": [
            ("name", str, "<instinct-name>"),
            ("description", str, "<one-line description>"),
            ("type", str, "instinct"),
            ("source_project", str, "<project-name>"),
            ("source_url", str, "https://github.com/owner/repo"),
            ("absorb_date", str, "YYYY-MM-DD"),
        ],
    },
}

def extract_frontmatter(content):
    """Extract YAML frontmatter between '---' delimiters."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    return match.group(1)

def parse_frontmatter(yaml_text):
    """Simple YAML parser for frontmatter (avoids PyYAML dependency)."""
    result = {}
    for line in yaml_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Handle lists
        list_match = re.match(r'^(\w+):\s*$', line)
        if list_match:
            key = list_match.group(1)
            result[key] = []
            continue
        # Handle list items
        list_item_match = re.match(r'^\s+-\s+(.+)$', line)
        if list_item_match and result and isinstance(list(list(result.keys())[-1:])[0], str):
            last_key = list(result.keys())[-1]
            if isinstance(result[last_key], list):
                result[last_key].append(list_item_match.group(1).strip())
                continue
        # Handle key: value
        kv_match = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)$', line)
        if kv_match:
            key = kv_match.group(1)
            val = kv_match.group(2).strip()
            # Remove quotes
            if val and val[0] in '"\'' and val[-1] == val[0]:
                val = val[1:-1]
            # Auto-convert numeric types
            if val and re.match(r'^-?\d+$', val):
                val = int(val)
            elif val and re.match(r'^-?\d+\.\d+$', val):
                val = float(val)
            elif val.lower() in ('true', 'false'):
                val = val.lower() == 'true'
            result[key] = val
    return result

def validate_file(filepath, schema_key=None):
    """Validate a single markdown file's frontmatter."""
    filename = os.path.basename(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine schema
    schema = SCHEMAS.get(filename) or SCHEMAS.get(schema_key)
    if not schema:
        return {"file": filepath, "status": "SKIP", "errors": ["No schema defined for this file type"]}

    # Extract frontmatter
    yaml_text = extract_frontmatter(content)
    if yaml_text is None:
        return {"file": filepath, "status": "FAIL", "errors": ["No YAML frontmatter found (must start and end with '---')"]}

    # Parse
    frontmatter = parse_frontmatter(yaml_text)

    # Validate required fields
    errors = []
    for field_name, field_type, example in schema.get("required", []):
        if field_name not in frontmatter:
            errors.append(f"MISSING required field '{field_name}' (example: {example})")
        elif not isinstance(frontmatter[field_name], field_type):
            # type check for tuples
            if isinstance(field_type, tuple):
                if not any(isinstance(frontmatter[field_name], t) for t in field_type):
                    errors.append(f"FIELD '{field_name}' has wrong type (expected {field_type}, got {type(frontmatter[field_name]).__name__})")
            else:
                errors.append(f"FIELD '{field_name}' has wrong type (expected {field_type.__name__}, got {type(frontmatter[field_name]).__name__})")

    # Validate optional fields if present
    for field_name, field_type, example in schema.get("optional", []):
        if field_name in frontmatter and not isinstance(frontmatter[field_name], field_type):
            if isinstance(field_type, tuple):
                type_names = "|".join(t.__name__ for t in field_type)
            else:
                type_names = field_type.__name__
            errors.append(f"OPTIONAL FIELD '{field_name}' has wrong type (expected {type_names})")

    # Depth validation
    if "depth" in frontmatter and frontmatter["depth"] not in ("L1", "L2", "L3", "L4", "L5", ""):
        errors.append(f"FIELD 'depth' must be L1-L5, got '{frontmatter['depth']}'")

    # Status validation
    valid_statuses = ("online", "built", "installed", "rejected", "deferred", "")
    if "status" in frontmatter and frontmatter["status"] not in valid_statuses:
        errors.append(f"FIELD 'status' must be one of {valid_statuses}, got '{frontmatter['status']}'")

    status = "PASS" if not errors else "FAIL"
    return {"file": filepath, "status": status, "errors": errors}

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <file_or_directory> [schema_name]")
        sys.exit(1)

    path = sys.argv[1]
    schema_key = sys.argv[2] if len(sys.argv) > 2 else None

    files_to_check = []
    if os.path.isdir(path):
        for f in os.listdir(path):
            if f.endswith('.md'):
                files_to_check.append(os.path.join(path, f))
    elif os.path.isfile(path) and path.endswith('.md'):
        files_to_check.append(path)
    else:
        print(f"❌ Invalid path: {path}")
        sys.exit(1)

    results = [validate_file(f, schema_key) for f in sorted(files_to_check)]

    # Summary
    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]
    skipped = [r for r in results if r["status"] == "SKIP"]

    print(f"\n{'='*60}")
    print(f"  absorb-osp Frontmatter Validation Report")
    print(f"{'='*60}")

    for r in results:
        if r["status"] == "PASS":
            print(f"  ✅ {os.path.basename(r['file'])}")
        elif r["status"] == "SKIP":
            print(f"  ⏭️  {os.path.basename(r['file'])} — {r['errors'][0]}")
        else:
            print(f"  ❌ {os.path.basename(r['file'])}")
            for err in r["errors"]:
                print(f"       • {err}")

    print(f"\n{'─'*60}")
    print(f"  Total: {len(results)}  |  ✅ Passed: {len(passed)}  |  ❌ Failed: {len(failed)}  |  ⏭️  Skipped: {len(skipped)}")
    print(f"{'='*60}\n")

    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
