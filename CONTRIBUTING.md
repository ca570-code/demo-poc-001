# Contributing

Thanks for contributing to this PoC.

## Local verification

Run the repository's verification command before opening a pull request:

```powershell
python verify_poc.py
```

This is the repository's test gate. A passing run must report `"status": "PASS"` and preserve the deterministic benchmark outputs.

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
