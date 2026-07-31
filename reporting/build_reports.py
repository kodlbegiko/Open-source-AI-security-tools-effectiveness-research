#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

TOOLS = ("gitleaks", "trufflehog", "detect-secrets")
DISPLAY = {"gitleaks": "Gitleaks 8.30.1", "trufflehog": "TruffleHog 3.96.0", "detect-secrets": "detect-secrets 1.5.0"}


def pct(value: float | None) -> str:
    return "N/A" if value is None else f"{100 * value:.1f}%"


def interval(value: list[float] | None) -> str:
    return "N/A" if not value else f"{100 * value[0]:.1f}%–{100 * value[1]:.1f}%"


def verdict(checks: dict[str, bool]) -> str:
    if all(checks.values()):
        return "SUPPORTED WITHIN THIS SYNTHETIC BENCHMARK"
    if any(checks.values()):
        return "PARTIALLY SUPPORTED"
    return "NOT SUPPORTED"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def table_rows(metrics: dict) -> list[str]:
    rows = []
    for tool in TOOLS:
        m = metrics["metrics"][tool]["split:confirmatory"]
        t = metrics["threshold_evaluation"][tool]
        rows.append(
            f"| {DISPLAY[tool]} | {pct(m['attack_block_rate'])} | {pct(m['benign_block_rate'])} | "
            f"{pct(m['tool_error_rate'])} | {pct(t['attack_block_rate_improvement'])} | "
            f"{verdict(t['checks'])} |"
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--freeze-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-url", required=True)
    args = parser.parse_args()

    artifact = Path(args.artifact_root)
    output = Path(args.output_root)
    reports = output / "reports"
    docs = output / "docs"
    data = output / "data"
    evidence = output / "evidence"
    for path in (reports, docs, data, evidence):
        path.mkdir(parents=True, exist_ok=True)

    metrics = load(artifact / "results/metrics/metrics.json")
    latency = load(artifact / "results/metrics/latency.json")
    summary = load(artifact / "generated/benchmark/summary.json")
    secondary = load(output / "results/metrics/secondary-subgroups.json")

    primary = metrics["primary_analysis"]["gitleaks"]
    primary_boot = primary["bootstrap"]
    primary_mc = primary["mcnemar"]
    primary_thresholds = metrics["threshold_evaluation"]["gitleaks"]
    primary_supported = all(primary_thresholds["checks"].values())

    if primary_supported:
        primary_verdict = "SUPPORTED WITHIN THIS SYNTHETIC BENCHMARK"
        overall = "CONDITIONAL GO AS A SECONDARY CONTROL; INSUFFICIENT EVIDENCE AS A PRIMARY SECURITY BOUNDARY"
    else:
        primary_verdict = "NOT SUPPORTED OR ONLY PARTIALLY SUPPORTED"
        overall = "NO-GO AS A PRIMARY SECURITY BOUNDARY; USE AS A SECONDARY CONTROL ONLY IF LOCAL COST-BENEFIT TESTING JUSTIFIES IT"

    common_header = (
        f"- Protocol freeze commit: `{args.freeze_sha}`\n"
        f"- Formal workflow run: `{args.run_id}`\n"
        f"- Formal workflow URL: {args.run_url}\n"
        f"- Benchmark manifest SHA256: `{summary['manifest_sha256']}`\n"
        f"- Confirmatory artifacts: **{summary['splits']['confirmatory']}**\n"
        f"- OOD artifacts: **{summary['splits']['out-of-distribution']}**\n"
        f"- Independent review: **NOT AVAILABLE**\n"
    )

    executive = f"""# Executive Summary

{common_header}
## Executive verdict

**Primary finding:** {primary_verdict}.

**Deployment decision:** {overall}.

The unique preregistered primary comparison was Gitleaks versus the frozen Regex baseline on 240 confirmatory unsafe artifacts. The observed absolute pass-through-rate reduction was **{pct(primary_boot['attack_pass_through_rate_reduction'])}**, with paired bootstrap 95% CI **{interval(primary_boot['ci95'])}**. The exact McNemar p-value was **{primary_mc['exact_p_value']:.6g}**.

## Confirmatory results

| Tool | Attack block rate | Benign block rate | Tool error rate | Improvement vs Regex | Threshold verdict |
|---|---:|---:|---:|---:|---|
{chr(10).join(table_rows(metrics))}

## Interpretation

These results measure deterministic synthetic credential-shaped artifacts in a controlled runner. They do not prove that any tool prevents real-world secret leakage, recognizes live credentials, understands Traditional Chinese semantics, or can serve as a complete security boundary. Provider verification was disabled, no independent annotator reviewed the generated core, and naturally occurring LLM outputs were not tested.
"""
    (reports / "executive-summary.md").write_text(executive, encoding="utf-8")

    final = f"""# Final Effectiveness Report

{common_header}
## 1. Executive verdict

**{overall}**

## 2. Research question

Do pinned open-source secret scanners reduce credential-bearing LLM/agent artifact pass-through relative to a transparent Regex baseline while maintaining acceptable benign blocking, OOD behavior, contextual language robustness and operational reliability?

## 3. Scope

The study evaluates Gitleaks, TruffleHog and detect-secrets as post-generation, pre-persistence secondary controls. It does not evaluate prompt injection, model alignment, live-secret validity, credential rotation or complete incident prevention.

## 4. Method

The deterministic benchmark contains {summary['total']} artifacts: {summary['splits']['confirmatory']} confirmatory and {summary['splits']['out-of-distribution']} OOD. English, Traditional Chinese and mixed contexts each contain {summary['languages']['en']} artifacts. SAFE and UNSAFE labels are balanced at {summary['labels']['SAFE']} each. Tool errors remain in the denominator under fail-open analysis.

## 5. Unique primary analysis

- Tool: Gitleaks 8.30.1
- Comparator: frozen Keyword/Regex baseline
- Population: 240 confirmatory UNSAFE artifacts
- Pass-through-rate reduction: **{pct(primary_boot['attack_pass_through_rate_reduction'])}**
- Paired bootstrap 95% CI: **{interval(primary_boot['ci95'])}**
- McNemar discordant pairs: **{primary_mc['discordant']}**
- Exact p-value: **{primary_mc['exact_p_value']:.6g}**
- Verdict: **{primary_verdict}**

## 6. Tool-by-tool confirmatory results

| Tool | Attack block rate | 95% CI | Benign block rate | Benign 95% CI | Error rate | Decision |
|---|---:|---:|---:|---:|---:|---|
"""
    for tool in TOOLS:
        m = metrics["metrics"][tool]["split:confirmatory"]
        decision = verdict(metrics["threshold_evaluation"][tool]["checks"])
        final += f"| {DISPLAY[tool]} | {pct(m['attack_block_rate'])} | {interval(m['attack_block_rate_ci95'])} | {pct(m['benign_block_rate'])} | {interval(m['benign_block_rate_ci95'])} | {pct(m['tool_error_rate'])} | {decision} |\n"

    final += "\n## 7. Language and OOD results\n\n"
    for tool in TOOLS:
        en = metrics["metrics"][tool]["split:confirmatory|language:en"]
        zh = metrics["metrics"][tool]["split:confirmatory|language:zh-TW"]
        mixed = metrics["metrics"][tool]["split:confirmatory|language:mixed"]
        ood = metrics["metrics"][tool]["split:out-of-distribution"]
        final += f"- **{DISPLAY[tool]}:** English attack block {pct(en['attack_block_rate'])}; Traditional Chinese {pct(zh['attack_block_rate'])}; mixed {pct(mixed['attack_block_rate'])}; OOD {pct(ood['attack_block_rate'])}.\n"

    final += f"""

Language here describes surrounding context, not credential syntax. Similar language results cannot be interpreted as semantic-language understanding.

## 8. Operational results

The formal artifact includes batch resource records and a 30-case latency sample after one unreported warm-up per tool. Summary values are retained in `results/metrics/latency.json`. Operational results are hardware- and runner-specific and should not be ranked across local and remote modes without context.

## 9. Secondary robustness analysis

Transformation, credential-family and fail-closed tables are in `results/metrics/secondary-subgroups.json`. They were prespecified conceptually but implemented after freeze under `PD-001`, before formal outcomes were inspected. They are secondary only and cannot support or overturn the primary verdict.

## 10. Validity threats

- Deterministic synthetic construction may be easier or less realistic than natural model output.
- Tool default rules may encode common provider formats similar to benchmark families.
- No independent human annotator or external reproducer was available.
- OOD is defined within synthetic construction families, not real distribution shift.
- GitHub-hosted runner evidence is reproducible but not an independent hardened laboratory.
- Provider verification was disabled, so detection does not establish live-secret validity.

## 11. Reproducibility

The study pins tool versions, release hashes, Python dependencies, runner family, benchmark digest, primary comparison and analysis seed. Raw credential-shaped cases exist only in the time-limited workflow artifact; the public repository retains reconstruction code, manifest hashes, normalized outcomes, metrics and reports. Reproducibility status is **PARTIALLY REPRODUCIBLE** until an independent environment reruns the frozen protocol.

## 12. Recommended use

Use a scanner, where supported by local results, as a layered pre-persistence check with fail-safe handling, secret vaulting, least privilege, rotation and incident response. Do not treat a scanner score or finding as proof that a credential is live.

## 13. Not recommended

Do not use any evaluated scanner as the sole security boundary, as evidence of multilingual semantic understanding, or as a substitute for preventing secrets from entering model context.

## 14. Protocol deviations

- Pre-freeze engineering events are recorded in `docs/protocol-deviations.md`.
- `PD-001` records the reporting-only implementation of prespecified secondary subgroup and fail-closed tables.

## 15. Next evidence required

An independently annotated set of naturally occurring or realistically sampled LLM/agent outputs, a blinded external rerun, and domain-specific deployment-cost measurements are required before a production recommendation can exceed conditional secondary-control use.
"""
    (reports / "final-report.md").write_text(final, encoding="utf-8")

    pilot = f"""# Pilot Report

The pilot split contains {summary['splits']['pilot']} artifacts. Pilot was used to validate acquisition, commands, adapters, structural redaction, cardinality, timeouts and evidence capture. Pilot results were not used to tune confirmatory labels, tool settings or deployment thresholds. Formal claims rely on the confirmatory and OOD splits only.
"""
    (reports / "pilot-report.md").write_text(pilot, encoding="utf-8")

    claim_lines = ["# Claim Verification", "", "Official tool claims are not treated as research facts.", "", "| Tool | Testable interpretation | Observed experiment | Verdict | Caveat |", "|---|---|---|---|---|"]
    claim_rows = []
    for tool in TOOLS:
        m = metrics["metrics"][tool]["split:confirmatory"]
        decision = verdict(metrics["threshold_evaluation"][tool]["checks"])
        claim_lines.append(f"| {DISPLAY[tool]} | Detect credential-bearing files under default offline scanning | Frozen confirmatory benchmark | {decision} | Synthetic, no provider verification |")
        claim_rows.append({"tool": DISPLAY[tool], "claim": "Detect secrets in files or repositories", "testable_interpretation": "Artifact-level BLOCK on policy-defined unsafe fixtures", "result_attack_block_rate": m["attack_block_rate"], "result_benign_block_rate": m["benign_block_rate"], "verdict": decision, "caveat": "Synthetic benchmark; live validity not tested"})
    (reports / "claim-verification.md").write_text("\n".join(claim_lines) + "\n", encoding="utf-8")
    with (data / "claim-verification.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(claim_rows[0]))
        writer.writeheader()
        writer.writerows(claim_rows)

    red_team = "# Robustness and Red-Team Results\n\nThis defensive robustness analysis uses OOD credential families, long-context dilution, Markdown/JSON/YAML contexts and runtime concatenation. Detailed secondary tables are in `results/metrics/secondary-subgroups.json`. No live target, credential verification or weaponizable bypass sequence was used. These tables are secondary under PD-001.\n"
    (reports / "red-team-results.md").write_text(red_team, encoding="utf-8")

    (docs / "validity-threats.md").write_text("# Validity Threats\n\n- Internal: adapter mapping, default-rule differences, hosted-runner variation.\n- Construct: finding is not equivalent to live-secret validation or harm prevention.\n- External: synthetic artifacts, no natural model-output sample, no external reproducer.\n- Conclusion: subgroup precision is limited and secondary analyses cannot override the primary comparison.\n", encoding="utf-8")
    (docs / "limitations.md").write_text("# Limitations\n\nThe benchmark is deterministic and synthetic; provider verification is disabled; independent annotation and review are unavailable; language is contextual rather than semantic; artifact retention is time-limited; and the study does not measure real incident reduction.\n", encoding="utf-8")
    (docs / "reproducibility.md").write_text(f"# Reproducibility\n\nStatus: **PARTIALLY REPRODUCIBLE**.\n\nFrozen commit: `{args.freeze_sha}`. Formal run: `{args.run_id}`. The repository pins scanner releases, asset hashes, Python wheels, runner family, benchmark digest and analysis seed. Independent reproduction remains unavailable.\n", encoding="utf-8")

    manifest = {
        "schema_version": "1.0",
        "protocol_freeze_commit": args.freeze_sha,
        "formal_run_id": args.run_id,
        "formal_run_url": args.run_url,
        "benchmark_manifest_sha256": summary["manifest_sha256"],
        "primary_verdict": primary_verdict,
        "productization_decision": overall,
        "reproducibility": "PARTIALLY_REPRODUCIBLE",
        "independent_review": "NOT_AVAILABLE",
        "files": [],
    }
    for path in sorted(list(reports.rglob("*")) + list(docs.rglob("*")) + list(data.rglob("*")) + list((output / "results/metrics").rglob("*"))):
        if path.is_file():
            manifest["files"].append({"path": path.relative_to(output).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size})
    (evidence / "evidence-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({"primary_verdict": primary_verdict, "productization_decision": overall, "reports": sorted(path.name for path in reports.iterdir())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
