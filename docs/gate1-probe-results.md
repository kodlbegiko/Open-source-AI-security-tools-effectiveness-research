# Gate 1 Scanner Execution Probe

## Scope

This probe tested whether three candidate secret and credential leakage detectors can be acquired at pinned versions, executed on a non-live synthetic fixture, and produce parseable evidence on a GitHub-hosted runner.

This is an **execution and comparability probe**, not an effectiveness result.

## Runs

| Run | Workflow run ID | Head SHA | Result | Finding |
|---|---:|---|---|---|
| 1 | `30603055550` | `48d6918c44b1c4127303d8034db26c5eec7c5ab5` | FAILURE | Tool acquisition succeeded; smoke-test orchestration failed because `detect-secrets` was invoked with an unsupported argument and zero-finding output assumptions were not isolated. |
| 2 | `30603231722` | `9d7ef8db740433e124a2018d16c7f952ddb3a2e3` | SUCCESS | All acquisition, execution, parsing, checksum and artifact-upload steps passed. |

The failed first run is retained as protocol-development evidence and was not deleted or relabeled.

## Pinned tools and acquisition evidence

| Tool | Version | Acquisition | Release-asset digest |
|---|---|---|---|
| Gitleaks | `8.30.1` | Official GitHub Release asset | `sha256:551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` |
| TruffleHog | `3.96.0` | Official GitHub Release asset | `sha256:7105f1cd6577f058a9e39d0578f1a99c8a1e481e4d3512cd8a09acfe22a0fdc0` |
| detect-secrets | `1.5.0` | PyPI package installed with exact version | Package version recorded; complete dependency freeze captured in the workflow artifact. |

Gitleaks and TruffleHog asset digests were obtained from the GitHub Releases API and verified before execution.

## Smoke-test outcome

| Tool | Command exit code | Parseable output | Findings on synthetic fixture |
|---|---:|---|---:|
| Gitleaks | 0 | yes | 4 |
| TruffleHog | 0 | yes | 3 |
| detect-secrets | 0 | yes | 1 |

The finding counts cannot be compared as effectiveness scores. The tools use different detectors, output semantics and duplication rules. The probe only demonstrates that each tool can execute and emit machine-readable results on the same controlled file input.

## Artifact integrity

- Artifact ID: `8782657968`
- Artifact name: `gate0-gate1-probe-evidence`
- Artifact size: `6947` bytes
- Artifact SHA256: `a801c02ac01e25444676cffc893731c3cc39f273cc851d65f3fba7e1ec2e8300`
- Artifact created: `2026-07-31T04:05:42Z`
- Artifact expiry: `2026-08-30T04:05:42Z`
- Internal checksum verification: **17/17 files passed**

## Safety and publication decision

The ephemeral fixture contains deterministic credential-shaped strings generated at runtime. They were not verified against any provider and are not intended to authenticate. Raw fixture and raw scanner outputs are retained only in the time-limited workflow artifact because committing them would trigger repository secret-scanning controls and would add unnecessary credential-shaped content to repository history.

The public repository records only:

- generator logic;
- pinned versions and release digests;
- redacted counts and exit codes;
- workflow and artifact identifiers;
- integrity hashes.

## Gate implication

The probe supports the following narrow conclusion:

> Gitleaks 8.30.1, TruffleHog 3.96.0 and detect-secrets 1.5.0 are executable on a common GitHub-hosted Linux runner, accept the same file-level fixture, and emit outputs that can be mapped by adapters.

It does **not** establish recall, false-positive rate, language generalization, out-of-distribution performance or deployment value. Those require a frozen protocol and independent benchmark.
