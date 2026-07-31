#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_pat", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("slack_bot", re.compile(r"xoxb-\d{12}-\d{12}-[A-Za-z0-9]{24}")),
    ("generic_hex_assignment", re.compile(r"(?i)(?:api[_-]?secret|secret|token)\s*[:=]\s*[\"']?[a-f0-9]{40,}")),
]


def load_manifest(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-root", default="generated/benchmark")
    parser.add_argument("--output-dir", default="results/normalized")
    args = parser.parse_args()
    root = Path(args.benchmark_root)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rows = load_manifest(root / "manifest.jsonl")

    no_tool = []
    regex = []
    for row in rows:
        common = {"case_id": row["case_id"], "split": row["split"], "tool_error": None}
        no_tool.append({**common, "tool": "no-security-tool", "normalized_action": "ALLOW", "finding_count": 0})
        text = (root / row["relative_path"]).read_text(encoding="utf-8")
        matches = [name for name, pattern in PATTERNS if pattern.search(text)]
        regex.append({
            **common,
            "tool": "keyword-regex-baseline",
            "normalized_action": "BLOCK" if matches else "ALLOW",
            "finding_count": len(matches),
            "matched_rules": matches,
        })

    for name, data in (("no-security-tool", no_tool), ("keyword-regex-baseline", regex)):
        (output / f"{name}.jsonl").write_text(
            "".join(json.dumps(item, sort_keys=True) + "\n" for item in data), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
