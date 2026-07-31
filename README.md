# Open-Source AI Security Tools Effectiveness Research

Research status: **FORMAL EVALUATION COMPLETED; FINAL REPOSITORY QC REQUIRED BEFORE RELEASE**

## Primary result

Gitleaks reduced attack pass-through by **17.9%** relative to the frozen Regex baseline on 240 confirmatory UNSAFE synthetic artifacts. Paired bootstrap 95% CI: **12.5%–23.3%**. Exact McNemar p-value: **6.98108e-11**.

Deployment decision: **CONDITIONAL GO AS A SECONDARY CONTROL; INSUFFICIENT EVIDENCE AS A PRIMARY SECURITY BOUNDARY**.

## Evidence identity

- Protocol freeze: `4535b0a244e4538b148de18618d7a82d3bb37fde`
- Authoritative execution: `b41edd68cf7384ba7982daf3a506b83c9ea5393b`
- Formal run: `30607636477`
- Artifact ID: `8784217517`
- Artifact digest: `sha256:296fb7ea1c01f82ac14b19c71ef4a85e3b015839e8cbf4ed542ac85f22f90b27`
- Benchmark manifest: `38059b47ea3b8217df38b90a4525286a18ca37b7bc136cfbbce5227aa6f54e27`
- Independent review: **NOT AVAILABLE**

## Scope warning

This is a controlled synthetic study of secret scanners used as post-generation file controls. It does not demonstrate real incident reduction, live-secret validity, natural LLM-output performance or multilingual semantic understanding. See `reports/final-report.md` and `docs/protocol-deviations.md`.
