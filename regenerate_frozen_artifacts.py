#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from benchmark_runner import compare, load, transform

ROOT = Path(__file__).resolve().parent


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_json(path, value):
    path.write_text(canon(value) + "\n", encoding="utf-8")


def sha256(path):
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_benchmark_report():
    actual = transform()
    expected = load("DEMO-GROUND-TRUTH-001.json")["records"]
    rows, numerator, denominator, accuracy = compare(actual, expected)
    pii_leak = any(
        rec.get("customer") not in (None, "[REDACTED]")
        or rec.get("customer_license") not in (None, "[REDACTED]")
        for rec in actual
    )
    return {
        "artifact_id": "DEMO-BENCHMARK-REPORT-001",
        "accuracy": accuracy,
        "critical_errors": [] if not pii_leak else ["CRIT-PII-001"],
        "denominator": denominator,
        "field_results": rows,
        "numerator": numerator,
        "scope_note": "Measures deterministic transformation against frozen expected canonical output; does not measure OCR extraction accuracy.",
        "version": "1.0.0",
    }


def build_redaction_report():
    actual = transform()
    pii_fields = load("DEMO-TAXONOMY-001.json")["pii_fields"]
    leaks = []
    for record in actual:
        for field in pii_fields:
            if record.get(field) not in (None, "[REDACTED]"):
                leaks.append(field)
    return {
        "artifact_id": "DEMO-REDACTION-REPORT-001",
        "pii_fields": pii_fields,
        "status": "PASS" if not leaks else "FAIL",
        "unredacted_leak_count": len(leaks),
        "version": "1.0.0",
    }


def build_expected_outputs():
    actual = transform()
    return {
        "DEMO-NORMALIZED-001.json": actual,
        "DEMO-BENCHMARK-REPORT-001.json": build_benchmark_report(),
        "DEMO-REDACTION-REPORT-001.json": build_redaction_report(),
    }


def build_evidence_manifest():
    manifest_path = ROOT / "DEMO-EVIDENCE-001.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact_names = [
        "DEMO-BENCHMARK-REPORT-001.json",
        "DEMO-DATASET-001.json",
        "DEMO-GROUND-TRUTH-001.json",
        "DEMO-NORMALIZED-001.json",
        "DEMO-REDACTION-REPORT-001.json",
        "DEMO-TAXONOMY-001.json",
        "DEMO-VALIDATION-RULES-001.json",
        "benchmark_runner.py",
    ]
    manifest["artifacts"] = [
        {"name": name, "sha256": sha256(ROOT / name)}
        for name in artifact_names
    ]
    return manifest


def ensure_frozen_files(write):
    expected = build_expected_outputs()
    mismatches = []
    for name, value in expected.items():
        path = ROOT / name
        expected_text = canon(value) + "\n"
        current_text = path.read_text(encoding="utf-8") if path.exists() else None
        if current_text == expected_text:
            continue
        mismatches.append(name)
        if write:
            write_json(path, value)

    evidence = build_evidence_manifest()
    evidence_text = canon(evidence) + "\n"
    manifest_path = ROOT / "DEMO-EVIDENCE-001.json"
    current_manifest = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else None
    if current_manifest != evidence_text:
        mismatches.append("DEMO-EVIDENCE-001.json")
        if write:
            write_json(manifest_path, evidence)

    if not mismatches:
        return 0
    if not write:
        print("Out-of-date generated artifacts:")
        for item in mismatches:
            print(f" - {item}")
        print("Run with --write to regenerate them.")
        return 1
    print("Regenerated:")
    for item in mismatches:
        print(f" - {item}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Regenerate deterministic JSON artifacts and update their evidence hashes.")
    parser.add_argument("--write", action="store_true", help="Write regenerated outputs and update the SHA-256 manifest.")
    parser.add_argument("--check", action="store_true", help="Check whether generated outputs are up to date without modifying files.")
    args = parser.parse_args()

    if not args.write and not args.check:
        parser.error("You must specify --write to modify files or --check to validate them.")

    if args.write and args.check:
        parser.error("Choose either --write or --check, not both.")

    return ensure_frozen_files(write=args.write)


if __name__ == "__main__":
    raise SystemExit(main())
