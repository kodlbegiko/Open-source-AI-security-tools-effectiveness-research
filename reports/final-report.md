# Final Effectiveness Report

- Protocol freeze commit: `4535b0a244e4538b148de18618d7a82d3bb37fde`
- Formal workflow run: `30607636477`
- Formal workflow URL: https://github.com/kodlbegiko/Open-source-AI-security-tools-effectiveness-research/actions/runs/30607636477
- Benchmark manifest SHA256: `38059b47ea3b8217df38b90a4525286a18ca37b7bc136cfbbce5227aa6f54e27`
- Confirmatory artifacts: **480**
- OOD artifacts: **180**
- Independent review: **NOT AVAILABLE**

## 1. Executive verdict

**CONDITIONAL GO AS A SECONDARY CONTROL; INSUFFICIENT EVIDENCE AS A PRIMARY SECURITY BOUNDARY**

## 2. Research question

Do pinned open-source secret scanners reduce credential-bearing LLM/agent artifact pass-through relative to a transparent Regex baseline while maintaining acceptable benign blocking, OOD behavior, contextual language robustness and operational reliability?

## 3. Scope

The study evaluates Gitleaks, TruffleHog and detect-secrets as post-generation, pre-persistence secondary controls. It does not evaluate prompt injection, model alignment, live-secret validity, credential rotation or complete incident prevention.

## 4. Method

The deterministic benchmark contains 780 artifacts: 480 confirmatory and 180 OOD. English, Traditional Chinese and mixed contexts each contain 260 artifacts. SAFE and UNSAFE labels are balanced at 390 each. Tool errors remain in the denominator under fail-open analysis.

## 5. Unique primary analysis

- Tool: Gitleaks 8.30.1
- Comparator: frozen Keyword/Regex baseline
- Population: 240 confirmatory UNSAFE artifacts
- Pass-through-rate reduction: **17.9%**
- Paired bootstrap 95% CI: **12.5%–23.3%**
- McNemar discordant pairs: **49**
- Exact p-value: **6.98108e-11**
- Verdict: **SUPPORTED WITHIN THIS SYNTHETIC BENCHMARK**

## 6. Tool-by-tool confirmatory results

| Tool | Attack block rate | 95% CI | Benign block rate | Benign 95% CI | Error rate | Decision |
|---|---:|---:|---:|---:|---:|---|
| Gitleaks 8.30.1 | 92.9% | 89.0%–95.5% | 0.0% | 0.0%–1.6% | 0.0% | SUPPORTED WITHIN THIS SYNTHETIC BENCHMARK |
| TruffleHog 3.96.0 | 65.8% | 59.6%–71.5% | 0.0% | 0.0%–1.6% | 0.0% | PARTIALLY SUPPORTED |
| detect-secrets 1.5.0 | 40.8% | 34.8%–47.1% | 10.0% | 6.8%–14.4% | 0.0% | PARTIALLY SUPPORTED |

## 7. Language and OOD results

- **Gitleaks 8.30.1:** English attack block 95.0%; Traditional Chinese 91.2%; mixed 92.5%; OOD 100.0%.
- **TruffleHog 3.96.0:** English attack block 65.0%; Traditional Chinese 66.2%; mixed 66.2%; OOD 33.3%.
- **detect-secrets 1.5.0:** English attack block 41.2%; Traditional Chinese 41.2%; mixed 40.0%; OOD 50.0%.


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

## PD-002 evidence-chain repair

Failed run `30607078461` completed the outcome calculations but did not publish immutable evidence because `command-log.txt` changed after checksum creation. `PD-002` changed only evidence finalization and workflow ordering. The benchmark, scanner versions, normalized decisions, thresholds, primary endpoint, bootstrap seed and McNemar test were unchanged. Under the registered first-successful-post-repair rule, run `30607636477` at commit `b41edd68cf7384ba7982daf3a506b83c9ea5393b` is authoritative. Artifact `8784217517` has digest `sha256:296fb7ea1c01f82ac14b19c71ef4a85e3b015839e8cbf4ed542ac85f22f90b27`.
