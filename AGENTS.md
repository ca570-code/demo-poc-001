# Repository Guidelines

## Project Structure & Module Organization

This is a self-contained Python proof of concept for deterministic record normalization, PII redaction, benchmark replay, and evidence hashing.

- `benchmark_runner.py` implements transformation and comparison logic.
- `verify_poc.py` is the end-to-end verifier: it checks artifact hashes, replays the benchmark, and writes the independent-verification result.
- `DEMO-DATASET-001.json` is the input fixture; `DEMO-TAXONOMY-001.json` and `DEMO-VALIDATION-RULES-001.json` define normalization and validation inputs.
- `DEMO-GROUND-TRUTH-001.json`, `DEMO-NORMALIZED-001.json`, and `DEMO-BENCHMARK-REPORT-001.json` are frozen expected outputs. `DEMO-EVIDENCE-001.json` holds SHA-256 evidence hashes.

Keep related artifacts at the repository root and retain the `DEMO-<PURPOSE>-001.json` naming pattern unless a new version is intentionally introduced.

## Build, Test, and Development Commands

No build step or external dependencies are required; use a supported local Python 3 interpreter.

```powershell
python benchmark_runner.py  # replay normalization and print canonical JSON
python verify_poc.py       # verify hashes and exact benchmark results
```

`verify_poc.py` exits nonzero when the replay fails and updates `DEMO-INDEPENDENT-VERIFICATION-001.json`. Review that generated file before committing it.

## Coding Style & Naming Conventions

Follow the existing standard-library-only approach. Use four-space indentation, UTF-8 text files, `snake_case` for functions and variables, and uppercase constants such as `ROOT`. Keep transformations deterministic: avoid timestamps, random values, environment-dependent paths, and unstable JSON serialization. Use `json.dumps(..., sort_keys=True, separators=(",", ":"))` when producing canonical evidence-bound JSON.

## Testing Guidelines

The executable verification is the test suite. Run `python verify_poc.py` after changing Python code or any tracked JSON fixture. A successful run must report `"status": "PASS"`, preserve exact normalized records and benchmark fields, and detect no PII leak. If fixture content changes intentionally, regenerate every affected frozen artifact and its evidence hash together; do not weaken the verifier to make a mismatch pass.

## Commit & Pull Request Guidelines

Git history is not present in this checkout, so no local commit convention can be inferred. Use short imperative subjects, for example `Add terpene alias normalization`. Keep each commit focused. Pull requests should state the behavior changed, list modified fixtures, include `python verify_poc.py` output, and explain any expected changes to hashes, normalized records, or benchmark accuracy.
