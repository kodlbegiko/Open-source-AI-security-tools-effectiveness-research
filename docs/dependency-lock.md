# Dependency Lock Evidence

- Workflow run: `30603875075`
- Head SHA: `93a2051f3ec8e6ba7fe9f04b0e945d74a82b842e`
- Artifact ID: `8782882766`
- Artifact SHA256: `6862b821769e5df0c26dc6891f1b59d067740ba40a917723d15f0e96263dc08f`
- Python: `3.13.14`
- Runner: `ubuntu-24.04`, x86_64
- Offline installation smoke test: `detect-secrets 1.5.0` passed

All seven wheels in `requirements.lock` were downloaded at exact versions, hashed, compared with PyPI JSON metadata, and installed into a clean virtual environment using `--no-index` and the local wheel directory.

| Package | Version | SHA256 |
|---|---|---|
| detect-secrets | 1.5.0 | `e24e7b9b5a35048c313e983f76c4bd09dad89f045ff059e354f9943bf45aa060` |
| PyYAML | 6.0.3 | `0f29edc409a6392443abf94b9cf89ce99889a1dd5376d94316ae5145dfedd5d6` |
| requests | 2.34.2 | `2a0d60c172f83ac6ab31e4554906c0f3b3588d37b5cb939b1c061f4907e278e0` |
| charset-normalizer | 3.4.9 | `84fd18bcc17526fc2b3c1af7d2b9217d32c9c04448c16ec693b9b4f1985c3d33` |
| idna | 3.18 | `7f952cbe720b688055e3f87de14f5c3e5fdaa8bc3928985c4077ca689de849a2` |
| urllib3 | 2.7.0 | `9fb4c81ebbb1ce9531cce37674bbc6f1360472bc18ca9a553ede278ef7276897` |
| certifi | 2026.7.22 | `62f22742b58a1a33014a2b6b706588a8d7e2a88ae7bd1a6ebe8c992928483775` |

The lock is platform-specific. A different Python minor version, operating system or architecture requires a separately verified lock rather than silent substitution.
