# Open-Source AI Security Tools Effectiveness Research

Research status: IN PROGRESS

No deployment recommendation or effectiveness conclusion is available yet.

This repository contains a public, reproducible, evidence-backed study of whether open-source AI security tools provide measurable security value under benign, adversarial, multilingual, out-of-distribution, and operational test conditions.

## Gate status

| Gate | Status |
|---|---|
| Gate 0 — Repository and environment | PASSED WITH LIMITATIONS |
| Gate 1 — Comparable category and tools | IN PROGRESS |
| Gate 2 — Protocol freeze | NOT STARTED |
| Gate 3 — Pilot | NOT STARTED |
| Gate 4 — Confirmatory evaluation | NOT STARTED |
| Gate 5 — Release qualification | NOT STARTED |

Gate 0 limitations include unavailable Docker/Podman isolation, unavailable GPU, restricted dependency installation and public network access from the execution container, and no currently verified autonomous tag/release path.

Evidence:

- [`docs/repository-audit.md`](docs/repository-audit.md)
- [`data/repository-audit.json`](data/repository-audit.json)
- [`docs/environment-audit.md`](docs/environment-audit.md)
- [`data/environment-audit.json`](data/environment-audit.json)

## Current phase

Candidate landscape and Gate 1 research-scope selection.

## Safety scope

All experiments must use controlled local or isolated environments, synthetic or openly licensed data, fictitious credentials and non-destructive payloads. This project does not authorize testing third-party services or publishing weaponizable bypass instructions.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
