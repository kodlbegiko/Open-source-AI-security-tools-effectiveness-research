# Threat Model

## Protected assets

- Credentials, tokens and API keys that may appear in model or agent output.
- Repositories, deployment artifacts, logs, tickets and user-visible responses that may persist those values.
- Downstream tools that could receive generated files or commands.
- Audit evidence needed to determine whether a control failed open.

## System boundary

```text
controlled synthetic prompt/context
→ LLM-like generated artifact fixture
→ scanner under test
→ normalized ALLOW/BLOCK/ERROR decision
→ simulated persistence or downstream release
```

No live model is required for the primary study. The generator deterministically constructs output artifacts representing plausible model or agent outputs. This isolates scanner effectiveness from model drift and API availability.

## Attacker and failure capabilities

The modeled failure may arise from:

1. a model reproducing a credential present in its context;
2. an agent writing a credential-shaped value to a file;
3. a user requesting configuration or deployment output that includes a secret;
4. an indirect instruction causing a generated artifact to contain a secret;
5. formatting, language or long context reducing scanner detection;
6. the scanner timing out, crashing, rejecting an input or silently returning no finding.

The study does not model an attacker validating credentials against providers, compromising third-party services, or repeatedly adapting to a known scanner through live feedback.

## Defense position

The formal tools are evaluated after artifact generation and before persistence, display, commit or downstream tool execution. They are not evaluated as model-alignment controls or prompt-injection detectors.

## Success and failure definitions

- **Attack success:** an `UNSAFE` artifact reaches the simulated downstream boundary without `BLOCK`.
- **Defense success:** an `UNSAFE` artifact produces `BLOCK` before the downstream boundary.
- **True positive:** `UNSAFE` and `BLOCK`.
- **False negative:** `UNSAFE` and any of `ALLOW`, `REVIEW`, `ERROR`, `TIMEOUT` or `UNSUPPORTED` under the primary fail-open analysis.
- **True negative:** `SAFE` and not `BLOCK`.
- **False positive:** `SAFE` and `BLOCK`.
- **Silent failure:** the process exits successfully or emits parseable output but fails to report a policy-defined credential.
- **Operational failure:** the process cannot start, exits unexpectedly, times out, emits unparsable output or does not support the artifact.
- **Fail-open:** operational failure is treated as not blocked. This is the primary safety analysis.
- **Fail-closed sensitivity:** operational failure is hypothetically treated as blocked. It is reported separately and cannot replace the primary result.

## Trust assumptions

- Generated credential-shaped values are non-live and never verified with a provider.
- Tool binaries and wheels are obtained only from pinned official release or package channels and hash-verified.
- GitHub-hosted runner isolation is trusted for this study, but is not equivalent to an independently controlled hardened laboratory.
- Scanner default rules are part of the tested release and are not manually improved using confirmatory cases.

## Out of scope

- Credential rotation, vaulting, least privilege and incident-response effectiveness.
- Whether a detected value is actually live.
- Prompt-injection or jailbreak prevention.
- PII detection.
- Malicious model-file or dependency scanning.
- Claims that a scanner is a complete security boundary.
