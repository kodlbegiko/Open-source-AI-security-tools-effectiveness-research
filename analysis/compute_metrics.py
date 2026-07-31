#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

BLOCK = "BLOCK"
TOOLS = ("gitleaks", "trufflehog", "detect-secrets")
PRIMARY_TOOL = "gitleaks"
SECONDARY_TOOLS = ("trufflehog", "detect-secrets")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def div(a: float, b: float) -> float | None:
    return a / b if b else None


def wilson(k: int, n: int, z: float = 1.959963984540054) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return [max(0.0, c - m), min(1.0, c + m)]


def confusion(cases: list[dict], results: dict[str, dict]) -> dict:
    tp = tn = fp = fn = errors = 0
    for case in cases:
        action = results[case["case_id"]]["normalized_action"]
        errors += action in {"ERROR", "TIMEOUT", "UNSUPPORTED"}
        blocked = action == BLOCK
        unsafe = case["risk_label"] == "UNSAFE"
        tp += unsafe and blocked
        fn += unsafe and not blocked
        fp += not unsafe and blocked
        tn += not unsafe and not blocked
    precision, recall = div(tp, tp + fp), div(tp, tp + fn)
    specificity = div(tn, tn + fp)
    f1 = div(2 * precision * recall, precision + recall) if precision is not None and recall is not None else None
    fpr, fnr = div(fp, fp + tn), div(fn, fn + tp)
    mcc_den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return {
        "n": len(cases), "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall, "specificity": specificity,
        "f1": f1, "false_positive_rate": fpr, "false_negative_rate": fnr,
        "balanced_accuracy": (recall + specificity) / 2 if recall is not None and specificity is not None else None,
        "mcc": div(tp * tn - fp * fn, mcc_den),
        "attack_block_rate": recall, "attack_block_rate_ci95": wilson(tp, tp + fn),
        "attack_pass_through_rate": fnr,
        "benign_block_rate": fpr, "benign_block_rate_ci95": wilson(fp, fp + tn),
        "tool_error_count": errors, "tool_error_rate": div(errors, len(cases)),
    }


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    x = (len(values) - 1) * q
    lo, hi = math.floor(x), math.ceil(x)
    return values[lo] if lo == hi else values[lo] * (hi - x) + values[hi] * (x - lo)


def paired_bootstrap(cases: list[dict], tool: dict[str, dict], baseline: dict[str, dict], iterations: int = 10000) -> dict:
    unsafe = [c for c in cases if c["risk_label"] == "UNSAFE"]
    tool_pass = [tool[c["case_id"]]["normalized_action"] != BLOCK for c in unsafe]
    base_pass = [baseline[c["case_id"]]["normalized_action"] != BLOCK for c in unsafe]
    observed = sum(base_pass) / len(unsafe) - sum(tool_pass) / len(unsafe)
    rng = random.Random(20260731)
    diffs = []
    for _ in range(iterations):
        indexes = [rng.randrange(len(unsafe)) for _ in unsafe]
        diffs.append(sum(base_pass[i] - tool_pass[i] for i in indexes) / len(unsafe))
    return {
        "n_unsafe": len(unsafe),
        "attack_pass_through_rate_reduction": observed,
        "ci95": [percentile(diffs, 0.025), percentile(diffs, 0.975)],
        "iterations": iterations,
        "seed": 20260731,
    }


def mcnemar(cases: list[dict], tool: dict[str, dict], baseline: dict[str, dict]) -> dict:
    baseline_only = tool_only = 0
    for case in cases:
        if case["risk_label"] != "UNSAFE":
            continue
        tool_blocks = tool[case["case_id"]]["normalized_action"] == BLOCK
        base_blocks = baseline[case["case_id"]]["normalized_action"] == BLOCK
        baseline_only += base_blocks and not tool_blocks
        tool_only += tool_blocks and not base_blocks
    n = baseline_only + tool_only
    if not n:
        p = 1.0
    else:
        k = min(baseline_only, tool_only)
        p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2**n))
    return {
        "baseline_only_blocks": baseline_only,
        "tool_only_blocks": tool_only,
        "discordant": n,
        "exact_p_value": p,
    }


def compare(cases: list[dict], tool: dict[str, dict], baseline: dict[str, dict], classification: str) -> dict:
    return {
        "classification": classification,
        "bootstrap": paired_bootstrap(cases, tool, baseline),
        "mcnemar": mcnemar(cases, tool, baseline),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="generated/benchmark/manifest.jsonl")
    ap.add_argument("--results-dir", default="results/normalized")
    ap.add_argument("--output", default="results/metrics/metrics.json")
    args = ap.parse_args()

    cases = load_jsonl(Path(args.manifest))
    tools: dict[str, dict[str, dict]] = {}
    for path in sorted(Path(args.results_dir).glob("*.jsonl")):
        rows = load_jsonl(path)
        if len(rows) != len(cases):
            raise SystemExit(f"{path}: expected {len(cases)} rows, got {len(rows)}")
        tools[rows[0]["tool"]] = {row["case_id"]: row for row in rows}
    required = set(TOOLS) | {"no-security-tool", "keyword-regex-baseline"}
    missing = required - set(tools)
    if missing:
        raise SystemExit(f"missing normalized results: {sorted(missing)}")

    groups: dict[str, list[dict]] = {"overall": cases}
    splits = sorted({c["split"] for c in cases})
    languages = sorted({c["language"] for c in cases})
    groups.update({f"split:{s}": [c for c in cases if c["split"] == s] for s in splits})
    groups.update({f"language:{lang}": [c for c in cases if c["language"] == lang] for lang in languages})
    groups.update({
        f"split:{s}|language:{lang}": [c for c in cases if c["split"] == s and c["language"] == lang]
        for s in splits for lang in languages
    })
    metrics = {tool: {name: confusion(subset, rows) for name, subset in groups.items()} for tool, rows in tools.items()}

    confirmatory = groups["split:confirmatory"]
    regex = tools["keyword-regex-baseline"]
    primary = {PRIMARY_TOOL: compare(confirmatory, tools[PRIMARY_TOOL], regex, "PRIMARY_CONFIRMATORY")}
    secondary = {tool: compare(confirmatory, tools[tool], regex, "SECONDARY_CONFIRMATORY") for tool in SECONDARY_TOOLS}

    ordered = sorted((result["mcnemar"]["exact_p_value"], tool) for tool, result in secondary.items())
    running = 0.0
    for index, (p_value, tool) in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered) - index) * p_value))
        secondary[tool]["mcnemar"]["holm_adjusted_p_value"] = running

    thresholds = {}
    regex_confirm = metrics["keyword-regex-baseline"]["split:confirmatory"]
    for tool in TOOLS:
        confirm = metrics[tool]["split:confirmatory"]
        ood = metrics[tool]["split:out-of-distribution"]
        en = metrics[tool]["split:confirmatory|language:en"]
        zh = metrics[tool]["split:confirmatory|language:zh-TW"]
        analysis = primary.get(tool) or secondary[tool]
        improvement = confirm["attack_block_rate"] - regex_confirm["attack_block_rate"]
        checks = {
            "attack_block_improvement_at_least_0_10": improvement >= 0.10,
            "comparison_ci_lower_above_zero": analysis["bootstrap"]["ci95"][0] > 0,
            "benign_block_rate_at_most_0_05": confirm["benign_block_rate"] <= 0.05,
            "benign_block_ci_upper_at_most_0_10": confirm["benign_block_rate_ci95"][1] <= 0.10,
            "ood_degradation_at_most_0_15": confirm["attack_block_rate"] - ood["attack_block_rate"] <= 0.15,
            "zh_tw_degradation_at_most_0_15": en["attack_block_rate"] - zh["attack_block_rate"] <= 0.15,
        }
        thresholds[tool] = {
            "classification": analysis["classification"],
            "attack_block_rate_improvement": improvement,
            "checks": checks,
            "all_deployment_thresholds_met": all(checks.values()),
        }

    output = {
        "schema_version": "1.1",
        "fail_open": True,
        "primary_endpoint": "paired reduction in attack pass-through rate versus keyword-regex-baseline on confirmatory unsafe cases",
        "primary_comparison": "gitleaks versus keyword-regex-baseline",
        "metrics": metrics,
        "primary_analysis": primary,
        "secondary_analysis": secondary,
        "threshold_evaluation": thresholds,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(primary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
