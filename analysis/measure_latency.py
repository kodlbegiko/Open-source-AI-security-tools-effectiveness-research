#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    position = (len(values) - 1) * q
    low = int(position)
    high = min(low + 1, len(values) - 1)
    fraction = position - low
    return values[low] * (1 - fraction) + values[high] * fraction


def command_for(tool: str, executable: str, fixture: Path, output: Path) -> list[str]:
    if tool == "gitleaks":
        return [executable, "dir", str(fixture.parent), "--no-banner", "--exit-code", "0", "--report-format", "json", "--report-path", str(output)]
    if tool == "trufflehog":
        return [executable, "filesystem", str(fixture), "--no-verification", "--json"]
    if tool == "detect-secrets":
        return [executable, "scan", "--all-files", str(fixture)]
    raise ValueError(tool)


def run_once(tool: str, executable: str, source: Path) -> tuple[float, int]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        fixture = root / source.name
        shutil.copy2(source, fixture)
        output = root / "output.json"
        command = command_for(tool, executable, fixture, output)
        started = time.perf_counter()
        completed = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        elapsed_ms = (time.perf_counter() - started) * 1000
        return elapsed_ms, completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="generated/benchmark/manifest.jsonl")
    parser.add_argument("--benchmark-root", default="generated/benchmark")
    parser.add_argument("--gitleaks", required=True)
    parser.add_argument("--trufflehog", required=True)
    parser.add_argument("--detect-secrets", required=True)
    parser.add_argument("--output", default="results/metrics/latency.json")
    args = parser.parse_args()

    cases = load_jsonl(Path(args.manifest))
    pilot = [case for case in cases if case["split"] == "pilot"]
    sample = []
    for language in ("en", "zh-TW", "mixed"):
        unsafe = [c for c in pilot if c["language"] == language and c["risk_label"] == "UNSAFE"][:5]
        safe = [c for c in pilot if c["language"] == language and c["risk_label"] == "SAFE"][:5]
        sample.extend(unsafe + safe)
    executables = {
        "gitleaks": args.gitleaks,
        "trufflehog": args.trufflehog,
        "detect-secrets": args.detect_secrets,
    }
    root = Path(args.benchmark_root)
    results = {}
    for tool, executable in executables.items():
        # One unreported warm-up execution.
        run_once(tool, executable, root / sample[0]["relative_path"])
        records = []
        for case in sample:
            elapsed, return_code = run_once(tool, executable, root / case["relative_path"])
            records.append({"case_id": case["case_id"], "latency_ms": elapsed, "return_code": return_code})
        latencies = [row["latency_ms"] for row in records]
        results[tool] = {
            "n": len(records),
            "mean_ms": statistics.fmean(latencies),
            "median_ms": statistics.median(latencies),
            "p95_ms": percentile(latencies, 0.95),
            "max_ms": max(latencies),
            "nonzero_return_codes": sum(row["return_code"] != 0 for row in records),
            "records": records,
        }
    output = {"schema_version": "1.0", "sample_definition": "30 pilot cases: 5 SAFE and 5 UNSAFE per language", "tools": results}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({tool: {k: v for k, v in data.items() if k != "records"} for tool, data in results.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
