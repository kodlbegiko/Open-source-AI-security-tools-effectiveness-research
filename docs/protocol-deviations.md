# Protocol Deviations

No post-freeze protocol deviation has occurred. This file is initialized before freeze.

## Pre-freeze engineering history

The following events occurred before protocol freeze and before any confirmatory or OOD scanner outcome was generated or inspected:

1. The empty repository bootstrap used three small Contents API commits rather than one atomic root commit because the available connector writes one file per operation.
2. The first Gate 1 smoke workflow failed after successful tool acquisition because detect-secrets was invoked with an unsupported argument and zero-finding output assumptions were not isolated. Failed run: `30603055550`.
3. GitHub Push Protection rejected a workflow revision containing credential-shaped literals. Fixtures were changed to deterministic runtime generation; no bypass was used.
4. A manually transferred Git blob for the benchmark generator was corrupted. CI detected invalid UTF-8. The file was restored through the GitHub Contents API, tests were rerun, and temporary repair assets were removed.
5. Confirmatory unsafe sample size increased from 120 to 240 before freeze after planning power was estimated at approximately 44% versus 81% under registered assumptions.
6. Statistical output changed before freeze to designate Gitleaks as the unique primary comparison and TruffleHog/detect-secrets as secondary comparisons.
7. Redaction preflight established that built-in scanner redaction was insufficient for retained JSON evidence. Formal evidence retention was changed before freeze to strict structural whitelists; unredacted temporary files are deleted before artifact upload. Failed preflight runs remain visible.
8. Unreferenced temporary Git blob objects expired before they could be attached to a tree. Protocol documents were therefore committed as explicit pre-freeze files, followed by a separate freeze-marker commit recording their final blob identities.

## Required format for future deviations

Every future entry must include:

- date and commit SHA;
- stage and affected files or data;
- reason;
- whether formal outcomes had been inspected;
- expected direction of bias;
- corrective action;
- whether pilot, confirmatory or OOD execution was invalidated and rerun.
