#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SENSITIVE_KEYS = {
    "Raw",
    "RawV2",
    "ExtraData",
    "VerificationError",
}


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    if input_path.exists():
        for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                records.append(redact(json.loads(line)))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSONL at line {line_number}: {exc}") from exc

    output_path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    print(json.dumps({"records": len(records), "sensitive_keys": sorted(SENSITIVE_KEYS)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
