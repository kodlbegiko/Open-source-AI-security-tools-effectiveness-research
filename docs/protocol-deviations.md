# Protocol Deviations

## PD-001 — Prespecified secondary reporting implemented after freeze

- Stage: post-freeze, before formal outcomes were inspected.
- Affected primary endpoint: no.
- Reason: the frozen protocol prespecified transformation, credential-family and fail-closed sensitivity tables, but the frozen primary metrics program did not emit those reporting tables.
- Corrective action: add a reporting-only program that derives the prespecified secondary tables from the frozen manifest and normalized outputs.
- Classification: `PRESPECIFIED_SECONDARY_ANALYSIS_IMPLEMENTED_POST_FREEZE`.
- Primary validity: unchanged. These tables cannot support or overturn the primary verdict.
- Machine-readable record: `evidence/protocol-deviation-001.json`.

## PD-002 — Evidence finalization and workflow ordering repair

- Date: 2026-07-31.
- Stage: post-freeze and after intermediate formal outcomes were visible in failed workflow logs.
- Affected files: `scripts/run_evaluation.sh`, the harvest workflow, reproducibility workflow and evidence-consistency workflow.
- Failed runs: Formal Evaluation `30607078461`; Reproducibility `30607078487`; Evidence Consistency `30607078497`.
- Root cause: `command-log.txt` remained open through process-substitution `tee` after `SHA256SUMS` was generated, so its digest changed before verification. The QC workflows also ran before the formal artifact had been harvested into the repository.
- Corrective action: execute all logged work through a finite pipeline, close `tee`, then generate and verify checksums. Harvest the first successful post-repair formal run whose head commit is an ancestor of the research branch. Run repository-level reproducibility and evidence consistency only after harvested results exist.
- Formal outcomes inspected: yes, from the failed run log.
- Expected bias direction: none. The benchmark, scanner versions, adapter mapping, labels, thresholds, primary comparison, fail-open policy, bootstrap seed and statistical tests are unchanged.
- Rerun rule: the first successful formal evaluation after this repair is authoritative; a later run may verify reproducibility but cannot replace it based on observed values.
- Primary validity: unchanged only if the rerun matches the frozen deterministic pipeline and raw-to-metric recomputation passes.
- Machine-readable record: `evidence/protocol-deviation-002.json`.

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
