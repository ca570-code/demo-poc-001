# DEMO_POC_001

[![Python verification](https://github.com/ca570-code/demo-poc-001/actions/workflows/verify.yml/badge.svg)](https://github.com/ca570-code/demo-poc-001/actions/workflows/verify.yml)

Minimum executable PoC for deterministic normalization, PII redaction, benchmark replay, and evidence hashing.

## Supported Python

Use Python 3.12 for local development. This project intentionally uses only the standard library.

## Run
`python verify_poc.py`

## Validate repository artifacts

Use the read-only contract check before review or CI:

```powershell
python validate_artifacts.py
```

This validates required top-level fields, artifact IDs, data types, internal consistency, and evidence-manifest references without modifying any files.

## Regenerate frozen artifacts

Use the repository's explicit regeneration command when intentionally changing deterministic outputs or the evidence manifest:

```powershell
python regenerate_frozen_artifacts.py --write
```

This script writes the derived frozen artifacts and refreshes the SHA-256 hashes in `DEMO-EVIDENCE-001.json`.
The command requires `--write`; without it, nothing is modified.

For CI and change validation, use:

```powershell
python regenerate_frozen_artifacts.py --check
```

## Current result
{
  "artifact_id": "DEMO-INDEPENDENT-VERIFICATION-001",
  "status": "PASS",
  "failures": [],
  "manifest_signature_status": "UNSIGNED",
  "note": "PASS verifies hash integrity and exact deterministic replay. Cryptographic signer verification is NOT performed while manifest is UNSIGNED."
}

## Important readiness boundary
This package does NOT yet prove OCR extraction accuracy because the original source images are not included in the supplied notebook.
It also does NOT provide cryptographic non-repudiation because no vendor signing key/identity was supplied.
The manifest is SHA-256 hash-bound and the replay test is executable.

Benchmark result: 89/89 fields = 100.000000% against frozen transformation ground truth.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

## Security

Please review [SECURITY.md](SECURITY.md) before reporting vulnerabilities.

## License

This project is licensed under the [MIT License](LICENSE).
