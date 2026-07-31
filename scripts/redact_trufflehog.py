#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def project(record: dict) -> dict:
    filesystem = (
        record.get("SourceMetadata", {})
        .get("Data", {})
        .get("Filesystem", {})
    )
    projected = {
        "DetectorType": record.get("DetectorType"),
        "DetectorName": record.get("DetectorName"),
        "DecoderName": record.get("DecoderName"),
        "Verified": record.get("Verified"),
        "SourceMetadata": {
            "Data": {
                "Filesystem": {
                    "file": filesystem.get("file"),
                }
            }
        },
    }
    return projected


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
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSONL at line {line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise SystemExit(f"record at line {line_number} is not an object")
            records.append(project(value))

    output_path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    print(json.dumps({
        "records": len(records),
        "retained_fields": ["DetectorType", "DetectorName", "DecoderName", "Verified", "SourceMetadata.Data.Filesystem.file"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
