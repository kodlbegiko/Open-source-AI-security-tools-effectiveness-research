# Evaluation Protocol

**Status before freeze:** DRAFT. This document becomes frozen only at the commit named `research: freeze effectiveness evaluation protocol`.

No confirmatory or OOD scanner outcome may be inspected before that commit.

## Research question

Under pinned offline settings, does Gitleaks reduce the pass-through rate of credential-bearing LLM-generated artifacts by at least 10 percentage points relative to a frozen transparent Regex baseline, while keeping benign blocking within the deployment thresholds?

TruffleHog and detect-secrets are prespecified secondary comparisons.

## Scope

- Category: secret and credential leakage detection.
- Position: post-generation, pre-persistence or pre-tool-call.
- Inputs: deterministic text/file artifacts representing plausible LLM or agent output.
- Intended security role: secondary control.
- No live model, provider API, real credential or third-party target.

## Conditions

| Condition | Frozen configuration |
|---|---|
| No Security Tool | always `ALLOW` |
| Keyword/Regex | source in `baselines/run_baselines.py`; frozen before formal execution |
| Gitleaks | `v8.30.1`; Linux x64 SHA256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`; default rules; directory scan |
| TruffleHog | `v3.96.0`; Linux amd64 SHA256 `7105f1cd6577f058a9e39d0578f1a99c8a1e481e4d3512cd8a09acfe22a0fdc0`; filesystem mode; verification disabled |
| detect-secrets | `1.5.0`; Python 3.13.14; exact wheel hashes in `requirements.lock`; default plugins |

No threshold tuning is permitted. Raw scanner outputs are reduced through strict field whitelists before retention. Unredacted Gitleaks and TruffleHog outputs exist only in runner temporary files and are deleted before artifact upload.

## Benchmark

The deterministic generator creates 780 artifacts:

| Split | Total | Unsafe | Safe | Per language |
|---|---:|---:|---:|---:|
| Development | 60 | 30 | 30 | 20 |
| Pilot | 60 | 30 | 30 | 20 |
| Confirmatory | 480 | 240 | 240 | 160 |
| Out of distribution | 180 | 90 | 90 | 60 |

Languages: English, Traditional Chinese and mixed context.

Expected manifest SHA256:

```text
38059b47ea3b8217df38b90a4525286a18ca37b7bc136cfbbce5227aa6f54e27
```

Development, pilot and confirmatory use AWS, GitHub, Slack and generic-hex constructions. OOD uses Stripe, Google API, GitLab, Twilio, OpenAI and SendGrid constructions. Official examples and repository fixtures do not enter confirmatory or OOD splits.

Raw credential-shaped fixtures are generated inside the runner and retained only in the time-limited evaluation artifact. Repository history contains generator logic, hashes and redacted summaries.

## Ground truth

Ground truth is derived from generator construction before scanner execution. Tested tools never label cases. Formal binary cases are `SAFE` or `UNSAFE`; see `labeling-guide.md`.

Independent human review is unavailable. This is a major limitation and prevents treating the deterministic benchmark as a substitute for external validation on naturally occurring outputs.

## Adapter contract

Each condition emits exactly one action per artifact:

```text
ALLOW | BLOCK | REVIEW | ERROR | TIMEOUT | UNSUPPORTED
```

- at least one policy-relevant finding maps to `BLOCK`;
- no finding maps to `ALLOW`;
- execution/parse failures map to failure actions;
- `REVIEW`, `ERROR`, `TIMEOUT` and `UNSUPPORTED` count as not blocked in the primary fail-open analysis;
- finding counts are not compared as effectiveness scores.

## Execution controls

- Runner: GitHub Actions `ubuntu-24.04`.
- Python: 3.13.14.
- Actions pinned by full commit SHA.
- Tool assets and wheels hash-verified.
- Batch timeout: 180 seconds per scanner.
- Per-case latency timeout: 30 seconds.
- Formal retry count: zero.
- Case ordering: deterministic.
- Warm-up: one unreported pilot artifact per tool before latency measurement.
- Formal execution: once per deterministic tool/case.

An infrastructure rerun is permitted only when no analyzable scanner outcome was produced, with the failed run retained and documented.

## Unique primary comparison

Gitleaks versus Keyword/Regex on the 240 confirmatory `UNSAFE` artifacts.

### Primary endpoint

```text
Regex pass-through rate − Gitleaks pass-through rate
```

### Primary inference

- paired bootstrap 95% CI, 10,000 iterations, seed 20260731;
- exact two-sided McNemar test;
- point estimate, CI, discordant counts and p-value.

No multiplicity correction applies to the unique primary comparison.

## Secondary analyses

- TruffleHog versus Regex.
- detect-secrets versus Regex.
- Holm correction across those two McNemar tests.
- Recall, precision, specificity, F1, FPR, FNR, balanced accuracy and MCC.
- Language, split and split-by-language subgroups.
- OOD, transformation and credential-family breakdowns.
- Fail-closed sensitivity.
- Latency, peak RSS, batch runtime and tool error rate.

Secondary analyses cannot override a failed primary endpoint.

## Deployment thresholds

All applicable conditions must hold:

1. attack block-rate improvement versus Regex at least 0.10;
2. paired 95% CI lower bound greater than zero;
3. confirmatory benign block-rate point estimate at most 0.05;
4. benign block-rate Wilson 95% CI upper bound at most 0.10;
5. OOD attack block-rate degradation at most 0.15;
6. Traditional Chinese attack block-rate degradation versus English at most 0.15;
7. no material undisclosed operational failure.

Statistical significance without practical thresholds is insufficient.

## Missing and error rules

- Every manifest case remains in the denominator.
- Missing rows fail analysis rather than shrink the sample.
- Process failure maps affected cases to `ERROR`.
- Timeout maps affected cases to `TIMEOUT`.
- Unparsable output is `ERROR`; stderr is retained.
- No imputation, case deletion or best-run selection.

## Pilot rules

Pilot may verify commands, adapters, schemas, redaction, artifact capture and runtime limits. It cannot change formal labels, select favorable families, tune rules using formal cases or alter deployment thresholds from observed effectiveness.

## Stop conditions

Stop a tool when release/hash cannot be verified, execution requires live credentials or provider verification, output cannot map deterministically, installation cannot be reproduced, or safety controls are inadequate.

Stop or downgrade the study when the manifest digest differs, formal data were used for tuning, a ground-truth defect changes labels, missing outputs cannot be reconstructed without outcome inspection, or runner/dependencies materially differ between conditions.

## Evidence

The formal workflow retains environment/version records, acquisition hashes, generated manifest/summary, structurally redacted raw outputs, normalized per-case outputs, metrics, latency, command log and SHA256SUMS.

Public reports distinguish `OBSERVED`, `DERIVED`, `INFERRED`, `CLAIMED` and `UNKNOWN`. No release occurs until results can be recomputed from retained evidence and all required checks pass.
