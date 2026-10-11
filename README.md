# DEMO_POC_001

Minimum executable PoC for deterministic normalization, PII redaction, benchmark replay, and evidence hashing.

## Run
`python verify_poc.py`

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
