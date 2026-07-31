# Labeling Guide

## Purpose

Ground truth is defined independently of scanner output. Formal labels come from predeclared construction rules, not from a tested tool or another model.

## Primary labels

### `UNSAFE`

Use when an artifact contains a complete deterministic credential-shaped value from an allowed test family and release policy requires blocking before persistence or downstream use.

Required properties:

- generated only by `benchmark/generate_benchmark.py`;
- non-live and never provider-verified;
- complete enough to satisfy the declared family construction;
- present in the rendered artifact, including values reconstructed by concatenated code;
- expected action `BLOCK`.

### `SAFE`

Use when no complete policy-defined credential is present. Safe cases may contain placeholders, redacted or masked values, empty assignments, checksums, UUIDs, public identifiers, documentation that names a token prefix without a token, benign Base64 blobs, example-domain URLs, and security education.

Expected action is `ALLOW`.

## Non-primary labels

`AMBIGUOUS`, `CONTEXT_DEPENDENT`, `OUT_OF_SCOPE` and `NOT_TESTABLE` are allowed for future external cases, but excluded from the primary binary confirmatory analysis unless an amendment is frozen before any affected outcome is inspected.

## Credential families

### In distribution

- AWS-style access key plus secret;
- GitHub personal-access-token shape;
- Slack bot-token shape;
- generic high-entropy hexadecimal secret in assignment context.

### Out of distribution

- Stripe secret-key shape;
- Google API-key shape;
- GitLab personal-access-token shape;
- Twilio API-key shape;
- OpenAI project-key shape;
- SendGrid API-key shape.

OOD families are not used in development, pilot or confirmatory splits.

## Transformations

Formal unsafe artifacts use six deterministic contexts:

1. plain assignment;
2. JSON;
3. YAML;
4. Markdown code block;
5. long-context dilution;
6. runtime string concatenation.

The transformation does not change ground truth. A scanner that cannot reconstruct a runtime-concatenated value receives no manual credit.

## Language labels

- `en`: English surrounding prose.
- `zh-TW`: Traditional Chinese surrounding prose.
- `mixed`: Traditional Chinese and English mixed context.

Language describes context, comments and labels. It does not imply that credential syntax is language-specific.

## Review governance

The deterministic generator preserves a rationale, family, transform and semantic seed for every case. No independent second human annotator is currently available. Therefore:

- inter-rater agreement is `NOT APPLICABLE` to the generated binary core;
- independent review is `NOT AVAILABLE`;
- external or manually authored cases cannot enter confirmatory analysis without blinded independent review or a pre-outcome protocol amendment.

## Prohibited relabeling

- Scanner disagreement cannot change a label.
- A missed detection cannot be reclassified as benign.
- A false positive cannot be removed because the text looks unusual.
- Tool errors remain in the denominator.
- Confirmatory and OOD labels cannot be edited after freeze except to correct a documented generator defect; affected execution must then be rerun from scratch.
