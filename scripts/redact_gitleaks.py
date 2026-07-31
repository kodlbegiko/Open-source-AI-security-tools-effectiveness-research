#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_FIELDS = {
    "Description",
    "StartLine",
    "EndLine",
    "StartColumn",
    "EndColumn",
    "File",
    "SymlinkFile",
    "Commit",
    "Entropy",
    "Author",
    "Email",
    "Date",
    "Message",
    "Tags",
    "RuleID",
    "Fingerprint",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = Path(args.input)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)

    records = json.loads(source.read_text(encoding="utf-8") or "[]") if source.exists() else []
    if not isinstance(records, list):
        raise SystemExit("Gitleaks output must be a JSON array")

    projected = [
        {key: record[key] for key in sorted(ALLOWED_FIELDS) if key in record}
        for record in records
    ]
    target.write_text(json.dumps(projected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(projected), "allowed_fields": sorted(ALLOWED_FIELDS)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
