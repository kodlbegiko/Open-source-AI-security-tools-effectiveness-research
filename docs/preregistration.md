# Preregistration

## Activation

This preregistration becomes active only at the commit named:

```text
research: freeze effectiveness evaluation protocol
```

That commit records the exact file/blob identities for the protocol, preregistration, threat model, labeling guide, sample-size analysis, research manifest, evaluation workflow and analysis code.

## Hypotheses

### H1 — Primary effectiveness

Gitleaks reduces confirmatory unsafe Attack Pass-Through Rate by at least 10 percentage points relative to the frozen Regex baseline, and the paired bootstrap 95% CI lower bound is greater than zero.

### H2 — Benign control

Gitleaks confirmatory benign block-rate point estimate is at most 5%, with Wilson 95% CI upper bound at most 10%.

### H3 — OOD robustness

Gitleaks OOD attack block rate is no more than 15 percentage points below its confirmatory attack block rate.

### H4 — Traditional Chinese contextual robustness

Gitleaks confirmatory Traditional Chinese attack block rate is no more than 15 percentage points below English. This does not imply Chinese semantic understanding.

### H5 — Secondary tools

TruffleHog and detect-secrets are compared with the same Regex baseline as secondary confirmatory analyses. Their exact McNemar p-values receive Holm correction across the two comparisons.

### H6 — Operational feasibility

Each formal tool installs from pinned, hash-verified artifacts, completes within frozen timeouts, emits parseable output for all cases and has a reportable error rate.

## Allowed verdicts

```text
SUPPORTED
PARTIALLY SUPPORTED
NOT SUPPORTED
INCONCLUSIVE
NOT TESTABLE
```

A hypothesis is `SUPPORTED` only when all named statistical and practical thresholds hold. A favorable p-value alone is insufficient.

## Data lock

- Confirmatory total: 480; unsafe 240; safe 240.
- OOD total: 180; unsafe 90; safe 90.
- Manifest SHA256: `38059b47ea3b8217df38b90a4525286a18ca37b7bc136cfbbce5227aa6f54e27`.
- Confirmatory and OOD artifacts cannot be used to edit Regex rules, adapters or tool settings.

## Primary analysis lock

- Tool: Gitleaks 8.30.1.
- Comparator: Keyword/Regex baseline.
- Population: confirmatory `UNSAFE` artifacts.
- Estimand: paired absolute reduction in pass-through rate.
- Interval: paired bootstrap, 10,000 iterations, seed 20260731.
- Test: exact two-sided McNemar, alpha 0.05.
- Missing/error treatment: fail open; no case deletion.

## Secondary analysis lock

- TruffleHog 3.96.0 versus Regex.
- detect-secrets 1.5.0 versus Regex.
- Holm adjustment over those two secondary tests.
- Descriptive and interval estimates by language, OOD status, transformation and family.
- Operational latency and resource summaries.

## Prohibited post-registration changes

- Changing the primary tool or comparator after viewing formal outcomes.
- Editing benchmark labels or deleting difficult cases.
- Adding tool-specific exceptions.
- Changing Regex rules using confirmatory or OOD cases.
- Replacing fail-open with fail-closed as the main result.
- Selecting the best workflow rerun.
- Presenting secondary or post-hoc results as the preregistered primary finding.

## Known limitations registered in advance

- Deterministic synthetic artifacts may not represent naturally occurring LLM outputs.
- No independent human annotator or external reviewer is currently available.
- Credential syntax is not inherently language-specific.
- Provider verification is disabled.
- GitHub-hosted infrastructure is not an independently controlled laboratory.
- Tool default rules may contain patterns similar to common provider formats.
- The study evaluates artifact-level blocking, not live credential validity or actual incident reduction.
