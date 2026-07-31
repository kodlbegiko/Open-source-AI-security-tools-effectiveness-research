#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

FAILURES = {"ERROR", "TIMEOUT", "UNSUPPORTED"}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def rates(cases: list[dict], results: dict[str, dict], fail_closed: bool = False) -> dict:
    tp = tn = fp = fn = errors = 0
    for case in cases:
        action = results[case["case_id"]]["normalized_action"]
        if action in FAILURES:
            errors += 1
        blocked = action == "BLOCK" or (fail_closed and action in FAILURES)
        unsafe = case["risk_label"] == "UNSAFE"
        if unsafe and blocked:
            tp += 1
        elif unsafe:
            fn += 1
        elif blocked:
            fp += 1
        else:
            tn += 1
    return {
        "n": len(cases),
        "unsafe_n": tp + fn,
        "safe_n": tn + fp,
        "attack_block_rate": tp / (tp + fn) if tp + fn else None,
        "attack_pass_through_rate": fn / (tp + fn) if tp + fn else None,
        "benign_block_rate": fp / (fp + tn) if fp + tn else None,
        "tool_error_count": errors,
        "fail_closed": fail_closed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cases = load_jsonl(Path(args.manifest))
    results_dir = Path(args.results_dir)
    tools: dict[str, dict[str, dict]] = {}
    for path in sorted(results_dir.glob("*.jsonl")):
        rows = load_jsonl(path)
        if not rows:
            continue
        tools[rows[0]["tool"]] = {row["case_id"]: row for row in rows}

    groups: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        groups[f"transformation:{case['transformation_type']}"] .append(case)
        groups[f"family:{case['secret_family']}"] .append(case)
        groups[f"difficulty:{case['difficulty']}"] .append(case)
        groups[f"context:{case['context_type']}"] .append(case)
        groups[f"split:{case['split']}|transformation:{case['transformation_type']}"] .append(case)
        groups[f"split:{case['split']}|family:{case['secret_family']}"] .append(case)

    output = {
        "schema_version": "1.0",
        "classification": "SECONDARY_POST_FREEZE_IMPLEMENTATION_OF_PRESPECIFIED_ANALYSIS",
        "primary_endpoint_affected": False,
        "protocol_deviation": "PD-001",
        "fail_open": {
            tool: {name: rates(subset, rows, False) for name, subset in sorted(groups.items())}
            for tool, rows in sorted(tools.items())
        },
        "fail_closed_sensitivity": {
            tool: {name: rates(subset, rows, True) for name, subset in sorted(groups.items())}
            for tool, rows in sorted(tools.items())
        },
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"groups": len(groups), "tools": sorted(tools)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
