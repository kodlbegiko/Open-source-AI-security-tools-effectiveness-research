# Research Question

## Selected security category

**Secret and Credential Leakage Detection used as an LLM output guardrail**

The evaluated tools are general-purpose secret scanners rather than AI-native security products. The study evaluates a specific deployment claim: whether these scanners can provide measurable security value when placed after an LLM or agent produces text/files and before that content is persisted, committed, displayed, or passed to a downstream tool.

## Primary research question

> Under pinned default or officially documented offline settings, do Gitleaks, TruffleHog and detect-secrets reduce the pass-through rate of credential-bearing LLM-generated text or files by at least 10 percentage points relative to a frozen transparent Keyword/Regex baseline, while keeping the benign block-rate point estimate at or below 5%?

## Primary unit of analysis

One independently labeled text artifact representing an LLM or agent output. An artifact may be plain text, Markdown, configuration, source code, logs, documentation, or structured text.

## Defense position

```text
LLM or agent output
→ secret scanner
→ ALLOW / BLOCK / ERROR
→ persistence, repository, user display, or downstream tool
```

The tool is evaluated as a **post-generation, pre-persistence or pre-tool-call secondary control**. The study does not assume that detection is equivalent to secret revocation, incident response, or complete prevention of disclosure.

## Ground-truth construct

### UNSAFE

An artifact contains a deterministic, non-live, credential-shaped value that satisfies a predeclared provider or generic-secret construction rule and is placed in a context where policy requires blocking before release.

### SAFE

An artifact contains no policy-defined credential. Safe cases will include:

- ordinary English, Traditional Chinese and mixed-language prose;
- documentation about credentials;
- redacted values and placeholders;
- hashes, UUIDs and non-secret high-entropy identifiers;
- security education and scanner documentation;
- quoted or escaped examples that policy explicitly permits;
- code and configuration without a secret.

`AMBIGUOUS` and `CONTEXT_DEPENDENT` cases are retained outside the primary binary analysis unless the frozen labeling guide defines a deterministic action.

## Formal tools

| Tool | Frozen candidate version | Execution mode for protocol development |
|---|---|---|
| Gitleaks | `v8.30.1` | local directory/file scan with default rules |
| TruffleHog | `v3.96.0` | filesystem scan with provider verification disabled |
| detect-secrets | `v1.5.0` | file scan with default plugins |

Exact commands, release digests, dependency hashes, timeouts and adapter mappings must be frozen at Gate 2. Versions shown here are selected candidates and may only change before protocol freeze with recorded evidence.

## Baselines

1. **No security tool** — every artifact is allowed.
2. **Frozen Keyword/Regex baseline** — transparent provider-format and assignment-context patterns developed only from development/pilot data.
3. **Optional transparent entropy baseline** — only if it remains materially simpler than the evaluated tools and is frozen before confirmatory testing.

## Primary endpoint

On confirmatory `UNSAFE` artifacts:

> Paired absolute difference in Attack Pass-Through Rate between each evaluated tool and the frozen Keyword/Regex baseline.

Primary safety analysis treats `REVIEW`, `ERROR`, `TIMEOUT` and `UNSUPPORTED` as not blocked (fail-open). A fail-closed sensitivity analysis will be reported separately.

## Deployment decision thresholds

Unless changed with a written justification before protocol freeze:

- Attack Block Rate improvement versus Regex: at least 10 percentage points;
- paired 95% confidence-interval lower bound: greater than 0;
- Benign Block Rate point estimate: no more than 5%;
- Benign Block Rate 95% confidence-interval upper bound: no more than 10%;
- OOD Attack Block Rate degradation: no more than 15 percentage points;
- Traditional Chinese versus English Attack Block Rate degradation: no more than 15 percentage points.

## Language dimension and limitation

The credential formats under test are mostly provider-defined strings and are not inherently English or Chinese. Language testing therefore evaluates:

- whether surrounding Traditional Chinese text changes detection or false-positive behavior;
- whether labels, comments, variable names and prose affect scanner output;
- whether translated security education, quoted examples and benign references are incorrectly blocked;
- whether mixed-language formatting and transformations change results.

The study must not interpret similar English and Traditional Chinese performance as evidence that a scanner understands Traditional Chinese semantics.

## Out-of-distribution dimension

OOD cases will use credential families, formatting contexts, benign lookalikes or transformation families not used to tune the Regex baseline or adapter logic. Official tool demos and repository fixtures are excluded from confirmatory and OOD splits.

## Safety constraints

- No real credentials, accounts, API keys or personal data.
- No provider verification requests during formal evaluation.
- Synthetic values are generated deterministically inside the controlled runner.
- Raw credential-shaped fixtures are not committed to public repository history when repository controls flag them; reconstruction logic, hashes and redacted summaries are published instead.
- No third-party system is tested.

## Claims explicitly outside scope

This study will not establish that:

- the tools prevent every secret leak;
- a detected value is live or exploitable;
- secret scanning is a primary security boundary;
- the tools understand multilingual semantics;
- scanner deployment replaces least privilege, key rotation, vaulting, incident response or model/data governance.
