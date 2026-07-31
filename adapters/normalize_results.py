#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_manifest(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def basename(value: str) -> str:
    return Path(value.replace("\\", "/")).name


def parse_gitleaks(path: Path) -> Counter[str]:
    data = json.loads(path.read_text() or "[]")
    return Counter(basename(item.get("File", "")) for item in data if item.get("File"))


def parse_trufflehog(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        file_name = (
            item.get("SourceMetadata", {})
            .get("Data", {})
            .get("Filesystem", {})
            .get("file")
        )
        if file_name:
            counts[basename(file_name)] += 1
    return counts


def parse_detect_secrets(path: Path) -> Counter[str]:
    data = json.loads(path.read_text())
    counts: Counter[str] = Counter()
    for file_name, findings in data.get("results", {}).items():
        counts[basename(file_name)] += len(findings)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True, choices=("gitleaks", "trufflehog", "detect-secrets"))
    parser.add_argument("--raw", required=True)
    parser.add_argument("--manifest", default="generated/benchmark/manifest.jsonl")
    parser.add_argument("--output", required=True)
    parser.add_argument("--exit-code", type=int, default=0)
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))
    raw_path = Path(args.raw)
    parser_map = {
        "gitleaks": parse_gitleaks,
        "trufflehog": parse_trufflehog,
        "detect-secrets": parse_detect_secrets,
    }
    if args.exit_code != 0:
        counts: Counter[str] = Counter()
        action = "ERROR"
    else:
        counts = parser_map[args.tool](raw_path)
        action = None

    output_rows = []
    for case in manifest:
        name = Path(case["relative_path"]).name
        count = counts[name]
        normalized = action or ("BLOCK" if count else "ALLOW")
        output_rows.append({
            "case_id": case["case_id"],
            "split": case["split"],
            "tool": args.tool,
            "normalized_action": normalized,
            "finding_count": count,
            "tool_error": None if args.exit_code == 0 else f"process_exit_{args.exit_code}",
        })
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in output_rows), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
