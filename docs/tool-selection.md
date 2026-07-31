# Tool and Category Selection

## Decision

- Selected category: **Secret and Credential Leakage Detection used as an LLM output guardrail**
- Formal tools: **Gitleaks 8.30.1, TruffleHog 3.96.0, detect-secrets 1.5.0**
- Baselines: **No Security Tool** and a frozen **Keyword/Regex baseline**
- Research question: see [`research-question.md`](research-question.md)
- Gate 1 verdict: **PASSED WITH LIMITATIONS**

This selection is a research-design decision, not a claim that the selected tools are effective or better than excluded candidates.

## Landscape screen

The verified landscape contains 20 official repositories across 8 categories. Categories were screened for task comparability, defense position, output normalization, ground-truth feasibility, execution feasibility and ability to complete a confirmatory study under the audited environment.

| Category | Decision | Main reason |
|---|---|---|
| Secret and Credential Leakage Detection | SELECTED | Three non-archived tools accept the same file-level input, can run on one controlled runner, emit machine-readable findings and support deterministic ground truth. |
| PII and Sensitive Data Detection | DEFERRED | Two candidates exist, but multilingual entity coverage and contextual PII policy would require a more complex annotation and model-resource study. |
| AI-Generated Code Security Scanning | DEFERRED | Tools are executable, but fair comparison requires language-specific vulnerability corpora and generated-code ground truth beyond the current bounded scope. |
| Input and Output Guardrails | DEFERRED | Candidate tasks and configurations are heterogeneous; one landscape candidate is archived and model/dependency acquisition is materially heavier. |
| Prompt Injection Detection | NOT SELECTED | The only seeded dedicated detector is archived; one tool is insufficient for the planned three-tool comparative design. |
| Model Output Validation | NOT SELECTED | Output-schema validation is a different construct from security-event blocking and cannot be fairly mixed with threat detectors. |
| AI Model and Dependency Supply Chain Security | DEFERRED | Candidate tools operate on different artifacts and security constructs: model scanning, pickle analysis, safe serialization and dependency CVEs. |
| AI Red-Team and Evaluation Frameworks | NOT SELECTED | These tools generate or orchestrate tests; they are not comparable runtime defenses and must not be ranked as blockers. |

## Why the selected tools are comparable

All three formal tools can be placed at the same defense point:

```text
LLM-generated text/file → scanner → normalized action → downstream release decision
```

The adapter contract will map tool output as follows:

- one or more policy-relevant findings: `BLOCK`;
- no findings: `ALLOW`;
- process failure: `ERROR`;
- timeout: `TIMEOUT`;
- unsupported input: `UNSUPPORTED`.

The primary analysis will not compare raw finding counts because detector duplication and taxonomy differ. The unit of comparison is the artifact-level release decision.

## Executability evidence

A GitHub Actions probe executed all three pinned tools against the same ephemeral synthetic fixture:

| Tool | Exit code | Parseable output | Probe findings |
|---|---:|---|---:|
| Gitleaks 8.30.1 | 0 | yes | 4 |
| TruffleHog 3.96.0 | 0 | yes | 3 |
| detect-secrets 1.5.0 | 0 | yes | 1 |

The different finding counts are not interpreted as effectiveness. Full redacted probe documentation is in [`gate1-probe-results.md`](gate1-probe-results.md).

## Weighted selection scores

Weights are those defined by the research mission. Scores measure **fitness for this study**, not product quality or security effectiveness.

| Criterion | Weight | Gitleaks | TruffleHog | detect-secrets |
|---|---:|---:|---:|---:|
| Problem importance | 15 | 14 | 14 | 14 |
| Claim testability | 10 | 10 | 10 | 10 |
| Deployment relevance | 10 | 10 | 10 | 9 |
| Execution feasibility | 10 | 10 | 10 | 10 |
| Open source and version fixability | 10 | 10 | 8 | 10 |
| Existing evidence gap | 10 | 9 | 9 | 9 |
| Tool comparability | 10 | 10 | 10 | 10 |
| Credible ground truth | 10 | 9 | 9 | 9 |
| Cross-language research value | 5 | 3 | 3 | 3 |
| Reproducibility | 5 | 5 | 4 | 4 |
| Safety and ethical controllability | 5 | 5 | 4 | 5 |
| **Total** | **100** | **95** | **91** | **93** |

## Score rationale and limitations

### Gitleaks

Strong fit because an official pinned binary and release digest are available, offline file scanning is direct, and output is readily normalized. Cross-language value is limited because most rules identify provider formats rather than natural-language meaning.

### TruffleHog

Strong fit because it scans the same artifact type and has broad provider detectors. Its optional credential verification is disabled for safety and reproducibility, so this study evaluates offline detection rather than live-secret verification. AGPL licensing and a more complex detector model reduce operational simplicity, not expected effectiveness.

### detect-secrets

Strong fit because it has a pinned package release, deterministic local execution and a distinct plugin/entropy approach. Its transitive Python dependencies must still be fully hash-locked at protocol freeze.

## Exclusions from formal comparison

- Archived tools are not automatically ineffective, but are excluded from the primary comparative set because maintenance and operational readiness are part of the deployment question.
- Red-team frameworks are excluded because generating a test is not the same as blocking a leak.
- PII tools are deferred because PII ground truth and multilingual context are materially different constructs.
- Code and model-supply-chain scanners are deferred because their units of analysis differ from text/file credential leakage.

## Gate 1 limitations

1. The formal versions are selected but complete dependency and artifact hashes are not yet frozen for every transitive dependency.
2. Official default configuration details and exact adapter commands still require protocol freeze.
3. The smoke fixture proves execution only; it provides no estimate of recall or false-positive rate.
4. Traditional Chinese relevance is primarily contextual false-positive and formatting behavior, not semantic-language comprehension.
5. TruffleHog provider verification will remain disabled in formal testing, limiting conclusions about live-secret verification.

## Gate 1 verdict

**PASSED WITH LIMITATIONS**

The minimum Gate 1 requirements are met:

- one threat category selected;
- common defense position and input type;
- three executable and non-archived tools;
- outputs can map to one adapter contract;
- No Security Tool and Keyword/Regex baselines defined.

The study may proceed to Gate 2 protocol development. No effectiveness conclusion is available.
