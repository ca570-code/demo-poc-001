# Contributing

Thanks for contributing to this PoC.

## Local verification

Run the repository's verification command before opening a pull request:

```powershell
python verify_poc.py
python -m unittest -q
```

This is the repository's test gate. A passing run must report `"status": "PASS"` and preserve the deterministic benchmark outputs.

## Regenerating frozen artifacts and evidence hashes

When a change intentionally alters normalization behavior or any tracked fixture, regenerate the derived outputs with:

```powershell
python regenerate_frozen_artifacts.py --write
```

This command writes the derived JSON outputs and refreshes the SHA-256 hashes in `DEMO-EVIDENCE-001.json`.
It requires the explicit `--write` flag; without that flag, the script does not modify files.

Use the non-mutating check for CI or pre-flight validation:

```powershell
python regenerate_frozen_artifacts.py --check
```

Do not weaken `verify_poc.py` to accept mismatches, disable deterministic checks, or skip SHA-256 validation. The verifier must continue to fail if the canonical outputs drift.

## Change expectations

- Keep the project standard-library-only unless a specific dependency is necessary.
- Preserve the `DEMO-<PURPOSE>-001.json` artifact naming pattern.
- Do not weaken deterministic checks or hash validation.
- If a fixture changes intentionally, update the affected frozen outputs and the evidence manifest together.

## Pull requests

- Keep changes focused.
- Include a short summary of what changed.
- State whether fixture or benchmark output changed.
- Include the `python verify_poc.py` result in the PR description.
