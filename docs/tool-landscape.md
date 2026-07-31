# Open-Source AI Security Tool Landscape

- Retrieved: `2026-07-31T04:10:24Z`
- Source: GitHub REST API and official repositories
- Candidate repositories: **20**
- Verified repositories: **20**
- Categories: **8**
- Archived repositories observed: **2**

> Inclusion in this landscape is not an effectiveness endorsement and does not imply formal evaluation.

## Category coverage

| Category | Candidates |
|---|---:|
| AI Model and Dependency Supply Chain Security | 4 |
| AI Red-Team and Evaluation Frameworks | 5 |
| AI-Generated Code Security Scanning | 2 |
| Input and Output Guardrails | 2 |
| Model Output Validation | 1 |
| PII and Sensitive Data Detection | 2 |
| Prompt Injection Detection | 1 |
| Secret and Credential Leakage Detection | 3 |

## Candidates

| Tool | Category | Repository | License | Head SHA | Latest release | Archived | Status |
|---|---|---|---|---|---|---:|---|
| LLM Guard | Input and Output Guardrails | `protectai/llm-guard` | MIT | `168c1034ffdb` | `—` | true | VERIFIED |
| NeMo Guardrails | Input and Output Guardrails | `NVIDIA-NeMo/Guardrails` | NOASSERTION | `891c13f64e45` | `v0.23.0` | false | VERIFIED |
| Guardrails AI | Model Output Validation | `guardrails-ai/guardrails` | Apache-2.0 | `798d2c457447` | `v0.10.2` | false | VERIFIED |
| Rebuff | Prompt Injection Detection | `protectai/rebuff` | Apache-2.0 | `4d2fe064abf1` | `v0.1.1` | true | VERIFIED |
| Microsoft Presidio | PII and Sensitive Data Detection | `data-privacy-stack/presidio` | MIT | `2bb88d2adca2` | `2.2.364` | false | VERIFIED |
| scrubadub | PII and Sensitive Data Detection | `LeapBeyond/scrubadub` | Apache-2.0 | `53772cbef417` | `v2.0.1` | false | VERIFIED |
| Gitleaks | Secret and Credential Leakage Detection | `gitleaks/gitleaks` | MIT | `b58d3f102cf3` | `v8.30.1` | false | VERIFIED |
| TruffleHog | Secret and Credential Leakage Detection | `trufflesecurity/trufflehog` | AGPL-3.0 | `d4d6275bc273` | `v3.96.0` | false | VERIFIED |
| detect-secrets | Secret and Credential Leakage Detection | `Yelp/detect-secrets` | Apache-2.0 | `5e141933554a` | `v1.5.0` | false | VERIFIED |
| ModelScan | AI Model and Dependency Supply Chain Security | `protectai/modelscan` | Apache-2.0 | `61fcec9c2a37` | `v0.8.8` | false | VERIFIED |
| Fickling | AI Model and Dependency Supply Chain Security | `trailofbits/fickling` | LGPL-3.0 | `913249db3bf1` | `v0.1.12` | false | VERIFIED |
| safetensors | AI Model and Dependency Supply Chain Security | `safetensors/safetensors` | Apache-2.0 | `6eb4dc9a28eb` | `v0.8.0` | false | VERIFIED |
| Bandit | AI-Generated Code Security Scanning | `PyCQA/bandit` | Apache-2.0 | `8f2376625ded` | `1.9.4` | false | VERIFIED |
| Semgrep | AI-Generated Code Security Scanning | `semgrep/semgrep` | LGPL-2.1 | `c83065a896af` | `v1.172.0` | false | VERIFIED |
| OSV-Scanner | AI Model and Dependency Supply Chain Security | `google/osv-scanner` | Apache-2.0 | `22613e79b261` | `v2.4.0` | false | VERIFIED |
| garak | AI Red-Team and Evaluation Frameworks | `NVIDIA/garak` | Apache-2.0 | `0b51f87acda1` | `v0.15.1` | false | VERIFIED |
| promptfoo | AI Red-Team and Evaluation Frameworks | `promptfoo/promptfoo` | MIT | `82ca3c24ec44` | `0.121.20` | false | VERIFIED |
| PyRIT | AI Red-Team and Evaluation Frameworks | `microsoft/PyRIT` | MIT | `2ee237d137f4` | `v1.0.1` | false | VERIFIED |
| Giskard | AI Red-Team and Evaluation Frameworks | `Giskard-AI/giskard-oss` | Apache-2.0 | `8aafe589261a` | `giskard-scan/v1.0.0b3` | false | VERIFIED |
| PurpleLlama | AI Red-Team and Evaluation Frameworks | `meta-llama/PurpleLlama` | NOASSERTION | `acfdd58f7c60` | `—` | false | VERIFIED |

## Interpretation limits

- Repository activity, releases and licensing are feasibility evidence, not security-effectiveness evidence.
- Different categories, defense locations and output semantics must not be combined into one effectiveness ranking.
- Exact formal tool versions will be frozen only after Gate 1 selection and before protocol freeze.
- Missing releases do not imply an ineffective tool; they indicate a packaging or versioning characteristic.
