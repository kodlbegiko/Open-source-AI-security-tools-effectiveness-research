# Executive Summary

- Protocol freeze commit: `4535b0a244e4538b148de18618d7a82d3bb37fde`
- Formal workflow run: `30607636477`
- Formal workflow URL: https://github.com/kodlbegiko/Open-source-AI-security-tools-effectiveness-research/actions/runs/30607636477
- Benchmark manifest SHA256: `38059b47ea3b8217df38b90a4525286a18ca37b7bc136cfbbce5227aa6f54e27`
- Confirmatory artifacts: **480**
- OOD artifacts: **180**
- Independent review: **NOT AVAILABLE**

## Executive verdict

**Primary finding:** SUPPORTED WITHIN THIS SYNTHETIC BENCHMARK.

**Deployment decision:** CONDITIONAL GO AS A SECONDARY CONTROL; INSUFFICIENT EVIDENCE AS A PRIMARY SECURITY BOUNDARY.

The unique preregistered primary comparison was Gitleaks versus the frozen Regex baseline on 240 confirmatory unsafe artifacts. The observed absolute pass-through-rate reduction was **17.9%**, with paired bootstrap 95% CI **12.5%–23.3%**. The exact McNemar p-value was **6.98108e-11**.

## Confirmatory results

| Tool | Attack block rate | Benign block rate | Tool error rate | Improvement vs Regex | Threshold verdict |
|---|---:|---:|---:|---:|---|
| Gitleaks 8.30.1 | 92.9% | 0.0% | 0.0% | 17.9% | SUPPORTED WITHIN THIS SYNTHETIC BENCHMARK |
| TruffleHog 3.96.0 | 65.8% | 0.0% | 0.0% | -9.2% | PARTIALLY SUPPORTED |
| detect-secrets 1.5.0 | 40.8% | 10.0% | 0.0% | -34.2% | PARTIALLY SUPPORTED |

## Interpretation

These results measure deterministic synthetic credential-shaped artifacts in a controlled runner. They do not prove that any tool prevents real-world secret leakage, recognizes live credentials, understands Traditional Chinese semantics, or can serve as a complete security boundary. Provider verification was disabled, no independent annotator reviewed the generated core, and naturally occurring LLM outputs were not tested.

## PD-002 evidence-chain repair

Failed run `30607078461` completed the outcome calculations but did not publish immutable evidence because `command-log.txt` changed after checksum creation. `PD-002` changed only evidence finalization and workflow ordering. The benchmark, scanner versions, normalized decisions, thresholds, primary endpoint, bootstrap seed and McNemar test were unchanged. Under the registered first-successful-post-repair rule, run `30607636477` at commit `b41edd68cf7384ba7982daf3a506b83c9ea5393b` is authoritative. Artifact `8784217517` has digest `sha256:296fb7ea1c01f82ac14b19c71ef4a85e3b015839e8cbf4ed542ac85f22f90b27`.
