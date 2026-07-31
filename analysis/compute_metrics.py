#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

POSITIVE_ACTION = "BLOCK"
FAIL_OPEN_ACTIONS = {"ALLOW", "REVIEW", "ERROR", "TIMEOUT", "UNSUPPORTED"}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def safe_div(a: float, b: float) -> float | None:
    return a / b if b else None


def wilson_ci(successes: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if total == 0:
        return None
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [max(0.0, center - margin), min(1.0, center + margin)]


def confusion(cases: list[dict], results: dict[str, dict]) -> dict:
    tp = tn = fp = fn = errors = 0
    for case in cases:
        row = results[case["case_id"]]
        action = row["normalized_action"]
        if action in {"ERROR", "TIMEOUT", "UNSUPPORTED"}:
            errors += 1
        blocked = action == POSITIVE_ACTION
        unsafe = case["risk_label"] == "UNSAFE"
        if unsafe and blocked:
            tp += 1
        elif unsafe and not blocked:
            fn += 1
        elif not unsafe and blocked:
            fp += 1
        else:
            tn += 1
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    specificity = safe_div(tn, tn + fp)
    f1 = safe_div(2 * precision * recall, precision + recall) if precision is not None and recall is not None and (precision + recall) else None
    fpr = safe_div(fp, fp + tn)
    fnr = safe_div(fn, fn + tp)
    balanced = (recall + specificity) / 2 if recall is not None and specificity is not None else None
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = safe_div(tp * tn - fp * fn, denominator)
    return {
        "n": len(cases), "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall, "specificity": specificity,
        "f1": f1, "false_positive_rate": fpr, "false_negative_rate": fnr,
        "balanced_accuracy": balanced, "mcc": mcc,
        "attack_block_rate": recall,
        "attack_block_rate_ci95": wilson_ci(tp, tp + fn),
        "attack_pass_through_rate": fnr,
        "benign_block_rate": fpr,
        "benign_block_rate_ci95": wilson_ci(fp, fp + tn),
        "tool_error_count": errors,
        "tool_error_rate": safe_div(errors, len(cases)),
    }


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    if not values:
        raise ValueError("empty values")
    index = (len(values) - 1) * q
    low, high = math.floor(index), math.ceil(index)
    if low == high:
        return values[low]
    return values[low] * (high - index) + values[high] * (index - low)


def paired_bootstrap_diff(cases: list[dict], tool: dict[str, dict], baseline: dict[str, dict], iterations: int = 10000) -> dict:
    unsafe = [case for case in cases if case["risk_label"] == "UNSAFE"]
    tool_pass = [1 if tool[c["case_id"]]["normalized_action"] != "BLOCK" else 0 for c in unsafe]
    base_pass = [1 if baseline[c["case_id"]]["normalized_action"] != "BLOCK" else 0 for c in unsafe]
    observed = sum(base_pass) / len(base_pass) - sum(tool_pass) / len(tool_pass)
    rng = random.Random(20260731)
    diffs = []
    for _ in range(iterations):
        indexes = [rng.randrange(len(unsafe)) for _ in unsafe]
        diffs.append(
            sum(base_pass[i] - tool_pass[i] for i in indexes) / len(indexes)
        )
    return {
        "n_unsafe": len(unsafe),
        "attack_pass_through_rate_reduction": observed,
        "ci95": [percentile(diffs, 0.025), percentile(diffs, 0.975)],
        "iterations": iterations,
        "seed": 20260731,
    }


def exact_mcnemar(cases: list[dict], a: dict[str, dict], b: dict[str, dict]) -> dict:
    unsafe = [case for case in cases if case["risk_label"] == "UNSAFE"]
    b01 = b10 = 0
    for case in unsafe:
        aid = a[case["case_id"]]["normalized_action"] == "BLOCK"
        bid = b[case["case_id"]]["normalized_action"] == "BLOCK"
        if not aid and bid:
            b01 += 1
        elif aid and not bid:
            b10 += 1
    n = b01 + b10
    if n == 0:
        p = 1.0
    else:
        k = min(b01, b10)
        tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
        p = min(1.0, 2 * tail)
    return {"baseline_only_blocks": b01, "tool_only_blocks": b10, "discordant": n, "exact_p_value": p}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="generated/benchmark/manifest.jsonl")
    parser.add_argument("--results-dir", default="results/normalized")
    parser.add_argument("--output", default="results/metrics/metrics.json")
    args = parser.parse_args()

    cases = load_jsonl(Path(args.manifest))
    result_files = sorted(Path(args.results_dir).glob("*.jsonl"))
    tools: dict[str, dict[str, dict]] = {}
    for path in result_files:
        rows = load_jsonl(path)
        if len(rows) != len(cases):
            raise SystemExit(f"{path}: expected {len(cases)} rows, got {len(rows)}")
        tool_name = rows[0]["tool"]
        tools[tool_name] = {row["case_id"]: row for row in rows}

    groups: dict[str, list[dict]] = {"overall": cases}
    for split in sorted({case["split"] for case in cases}):
        groups[f"split:{split}"] = [case for case in cases if case["split"] == split]
    for language in sorted({case["language"] for case in cases}):
        groups[f"language:{language}"] = [case for case in cases if case["language"] == language]
    for split in sorted({case["split"] for case in cases}):
        for language in sorted({case["language"] for case in cases}):
            groups[f"split:{split}|language:{language}"] = [
                case for case in cases if case["split"] == split and case["language"] == language
            ]

    metrics = {
        tool: {group: confusion(subset, results) for group, subset in groups.items()}
        for tool, results in tools.items()
    }

    confirmatory = groups["split:confirmatory"]
    regex = tools["keyword-regex-baseline"]
    primary = {}
    for tool in ("gitleaks", "trufflehog", "detect-secrets"):
        primary[tool] = {
            "bootstrap": paired_bootstrap_diff(confirmatory, tools[tool], regex),
            "mcnemar": exact_mcnemar(confirmatory, tools[tool], regex),
        }

    # Holm-adjust the three prespecified McNemar p-values.
    ordered = sorted((data["mcnemar"]["exact_p_value"], tool) for tool, data in primary.items())
    running = 0.0
    m = len(ordered)
    for index, (p_value, tool) in enumerate(ordered):
        adjusted = min(1.0, (m - index) * p_value)
        running = max(running, adjusted)
        primary[tool]["mcnemar"]["holm_adjusted_p_value"] = running

    threshold_evaluation = {}
    regex_confirm = metrics["keyword-regex-baseline"]["split:confirmatory"]
    for tool in ("gitleaks", "trufflehog", "detect-secrets"):
        confirm = metrics[tool]["split:confirmatory"]
        ood = metrics[tool]["split:out-of-distribution"]
        english = metrics[tool]["split:confirmatory|language:en"]
        zh = metrics[tool]["split:confirmatory|language:zh-TW"]
        bootstrap = primary[tool]["bootstrap"]
        improvement = confirm["attack_block_rate"] - regex_confirm["attack_block_rate"]
        benign_ci = confirm["benign_block_rate_ci95"]
        checks = {
            "attack_block_improvement_at_least_0_10": improvement >= 0.10,
            "primary_ci_lower_above_zero": bootstrap["ci95"][0] > 0,
            "benign_block_rate_at_most_0_05": confirm["benign_block_rate"] <= 0.05,
            "benign_block_ci_upper_at_most_0_10": benign_ci is not None and benign_ci[1] <= 0.10,
            "ood_degradation_at_most_0_15": (confirm["attack_block_rate"] - ood["attack_block_rate"]) <= 0.15,
            "zh_tw_degradation_at_most_0_15": (english["attack_block_rate"] - zh["attack_block_rate"]) <= 0.15,
        }
        threshold_evaluation[tool] = {
            "attack_block_rate_improvement": improvement,
            "confirmatory_attack_block_rate": confirm["attack_block_rate"],
            "confirmatory_benign_block_rate": confirm["benign_block_rate"],
            "ood_attack_block_rate": ood["attack_block_rate"],
            "english_attack_block_rate": english["attack_block_rate"],
            "zh_tw_attack_block_rate": zh["attack_block_rate"],
            "checks": checks,
            "all_deployment_thresholds_met": all(checks.values()),
        }

    output = {
        "schema_version": "1.0",
        "primary_endpoint": "paired reduction in attack pass-through rate versus keyword-regex-baseline on confirmatory unsafe cases",
        "fail_open": True,
        "metrics": metrics,
        "primary_analysis": primary,
        "threshold_evaluation": threshold_evaluation,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(primary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
