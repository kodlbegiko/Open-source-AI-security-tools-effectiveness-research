# Execution Environment Audit

- Audit time: 2026-07-31T11:53:00+08:00
- Verdict: **GO WITH LIMITATIONS**
- Evidence type: commands executed in the active managed Linux container plus successful GitHub connector writes

## System inventory

| Item | Observed value |
|---|---|
| Operating system | Debian GNU/Linux 13.3 (trixie) |
| Kernel | Linux 6.12.13 x86_64 |
| CPU | 5 vCPU, AMD EPYC 9V74 |
| Memory | 5.9 GiB total, approximately 5.1 GiB available during audit |
| Swap | 0 |
| Storage | 63 GiB filesystem, approximately 39 GiB available |
| GPU | Not available; `nvidia-smi` absent |
| Python | 3.13.5 |
| Node.js | 22.16.0 |
| npm | 10.9.2 |
| Git | 2.47.3 |
| GitHub CLI | Not installed |
| Docker | Not installed |
| Podman | Not installed |
| Shell | `/bin/bash` |

## Preinstalled analysis capabilities

The following Python packages were importable without installation:

| Package | Version/status |
|---|---|
| pytest | 9.0.2 |
| pandas | 2.2.3 |
| scipy | 1.17.0 |
| matplotlib | 3.10.8 |
| pydantic | 2.13.4 |
| numpy | 2.3.5 |
| scikit-learn | 1.8.0 |
| torch | 2.10.0+cpu |
| nltk | 3.9.2 |
| jsonschema | 4.26.0 |
| psutil | 7.2.2 |

Representative AI-security packages not present included `transformers`, `onnxruntime`, `presidio_analyzer`, `nemoguardrails`, `llm_guard`, and `guardrails`.

## Executed capability tests

| Test | Result | Evidence summary |
|---|---|---|
| Python CLI execution | PASS | Python scripts executed |
| Unit tests | PASS | `pytest`: 1 passed |
| JSON generation | PASS | valid JSON artifact created |
| CSV generation | PASS | CSV artifact created |
| Markdown generation | PASS | Markdown artifact created |
| Statistical analysis | PASS | SciPy binomial test executed |
| Data-frame processing | PASS | pandas calculation executed |
| Chart generation | PASS | matplotlib PNG created |
| Schema/model validation | PASS | Pydantic model validated |
| SHA256 calculation | PASS | Python and `sha256sum` paths worked |
| ZIP creation and verification | PASS | Python zip plus `zip`/`unzip -t` worked |
| Local HTTP service | PASS | `python -m http.server`; HTTP 200 received |
| Node runtime | PASS | Node generated a JSON artifact |
| npm project initialization | PASS | `npm init -y` completed |
| Local Git initialize/commit | PASS | repository initialized and committed |
| Local Git branch creation | PASS | test branch created |
| GitHub repository write | PASS | files committed through GitHub connector |
| GitHub branch creation | PASS | `research/effectiveness-study` created |
| Python package installation | FAIL | configured package gateway returned no matching `pytest` distribution |
| Node package installation | FAIL | configured package gateway returned HTTP 404 for `lodash@4.17.21` |
| DNS to `github.com` | FAIL | temporary failure in name resolution |
| DNS to `pypi.org` | FAIL | temporary failure in name resolution |
| DNS to `registry.npmjs.org` | FAIL | temporary failure in name resolution |
| HTTPS to GitHub from container | FAIL | DNS resolution failure |
| Git clone from GitHub | FAIL | could not resolve `github.com` |
| Docker execution | FAIL | Docker absent |
| Podman execution | FAIL | Podman absent |
| GPU execution | NOT AVAILABLE | no GPU exposed |
| Public model download | NOT AVAILABLE | container network resolution unavailable |
| GitHub Actions | NOT YET TESTED | no workflow run yet |
| GitHub Tag/Release | NOT VERIFIED | connector lacks tag/release action; `gh` absent |

## Network and package-management finding

The container is routed to internal package gateways but the requested public packages were unavailable in those gateways during the audit. Direct DNS resolution for public GitHub, PyPI and npm hosts also failed. Therefore this environment cannot assume on-demand dependency installation, repository cloning or model download.

This is an observed environment constraint, not evidence that a candidate tool is ineffective.

## Isolation and supply-chain finding

The active workload already runs inside a managed container, but it cannot create nested Docker or Podman containers. Consequently, arbitrary third-party install scripts or untrusted tools cannot automatically receive the per-tool isolation required by the research protocol.

Candidate tools must therefore satisfy at least one of these conditions until stronger isolation is available:

1. auditable source can be obtained through a controlled channel and runs with existing dependencies;
2. the tool is a portable binary or self-contained artifact whose checksum and provenance can be verified;
3. execution is limited to a separately available trusted sandbox;
4. the tool is marked `NOT TESTABLE UNDER AVAILABLE ISOLATION`.

## Research impact

### Work that can proceed now

- repository and evidence structure
- candidate landscape research using official public sources
- protocol, schemas and baselines
- benchmark construction and validation
- CPU-based Python harness development
- unit tests and statistical analysis
- local services and deterministic fixture runs
- GitHub commits, branches and pull requests through the connector

### Work requiring constraint-aware selection or another execution path

- tools requiring uninstalled packages
- tools requiring model downloads
- tools requiring Docker images
- GPU-dependent tools
- tools requiring unrestricted external APIs
- final autonomous tag and release creation

## Gate 0 decision

**GO WITH LIMITATIONS**

The environment is sufficient to initialize the research, build the benchmark and harness, run baselines, perform analysis and publish branch/PR evidence. It is not sufficient to promise evaluation of arbitrary open-source AI-security tools. Gate 1 must select tools compatible with the observed dependency, network and isolation constraints, or explicitly downgrade them to installation failure or not-testable status.
