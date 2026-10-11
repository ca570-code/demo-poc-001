#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = {
    "dataset": ROOT / "DEMO-DATASET-001.json",
    "taxonomy": ROOT / "DEMO-TAXONOMY-001.json",
    "validation_rules": ROOT / "DEMO-VALIDATION-RULES-001.json",
    "normalized": ROOT / "DEMO-NORMALIZED-001.json",
    "ground_truth": ROOT / "DEMO-GROUND-TRUTH-001.json",
    "benchmark": ROOT / "DEMO-BENCHMARK-REPORT-001.json",
    "evidence": ROOT / "DEMO-EVIDENCE-001.json",
    "independent_verification": ROOT / "DEMO-INDEPENDENT-VERIFICATION-001.json",
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing required artifact: {path.name}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {path.name}: {exc.msg} (line {exc.lineno}, column {exc.colno})")


def describe_expected(expected_type):
    if isinstance(expected_type, tuple):
        return " or ".join(t.__name__ for t in expected_type)
    return expected_type.__name__


def require_type(errors, label, value, expected_type, *, allow_none=False):
    if value is None and allow_none:
        return
    if not isinstance(value, expected_type):
        errors.append(f"{label}: expected {describe_expected(expected_type)}, found {type(value).__name__}")


def validate_dataset(data, errors):
    require_type(errors, "DEMO-DATASET-001.json artifact_id", data.get("artifact_id"), str)
    if data.get("artifact_id") != "DEMO-DATASET-001":
        errors.append("DEMO-DATASET-001.json artifact_id must be 'DEMO-DATASET-001'")

    require_type(errors, "DEMO-DATASET-001.json record_count", data.get("record_count"), int)
    records = data.get("records")
    require_type(errors, "DEMO-DATASET-001.json records", records, list)
    if isinstance(records, list) and isinstance(data.get("record_count"), int):
        if len(records) != data["record_count"]:
            errors.append(
                "DEMO-DATASET-001.json record_count must equal len(records) "
                f"({data['record_count']} != {len(records)})"
            )
    if isinstance(records, list):
        for idx, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"DEMO-DATASET-001.json records[{idx}] must be an object")
                continue
            if "image_filename" in record and not isinstance(record["image_filename"], str):
                errors.append(f"DEMO-DATASET-001.json records[{idx}].image_filename must be a string")

    require_type(errors, "DEMO-DATASET-001.json source", data.get("source"), str)
    require_type(errors, "DEMO-DATASET-001.json version", data.get("version"), str)


def validate_taxonomy(data, errors):
    require_type(errors, "DEMO-TAXONOMY-001.json artifact_id", data.get("artifact_id"), str)
    if data.get("artifact_id") != "DEMO-TAXONOMY-001":
        errors.append("DEMO-TAXONOMY-001.json artifact_id must be 'DEMO-TAXONOMY-001'")

    require_type(errors, "DEMO-TAXONOMY-001.json date_format", data.get("date_format"), str)
    require_type(errors, "DEMO-TAXONOMY-001.json identifier_fields", data.get("identifier_fields"), list)
    require_type(errors, "DEMO-TAXONOMY-001.json pii_fields", data.get("pii_fields"), list)
    require_type(errors, "DEMO-TAXONOMY-001.json shape_rules", data.get("shape_rules"), list)
    require_type(errors, "DEMO-TAXONOMY-001.json terpene_aliases", data.get("terpene_aliases"), dict)
    require_type(errors, "DEMO-TAXONOMY-001.json version", data.get("version"), str)

    if isinstance(data.get("pii_fields"), list):
        for field in data["pii_fields"]:
            if not isinstance(field, str):
                errors.append("DEMO-TAXONOMY-001.json pii_fields must be strings")
                break

    if isinstance(data.get("terpene_aliases"), dict):
        for key, value in data["terpene_aliases"].items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append("DEMO-TAXONOMY-001.json terpene_aliases entries must map strings to strings")
                break


def validate_validation_rules(data, errors):
    require_type(errors, "DEMO-VALIDATION-RULES-001.json artifact_id", data.get("artifact_id"), str)
    if data.get("artifact_id") != "DEMO-VALIDATION-RULES-001":
        errors.append("DEMO-VALIDATION-RULES-001.json artifact_id must be 'DEMO-VALIDATION-RULES-001'")

    require_type(errors, "DEMO-VALIDATION-RULES-001.json benchmark_dispositions", data.get("benchmark_dispositions"), list)
    require_type(errors, "DEMO-VALIDATION-RULES-001.json critical_errors", data.get("critical_errors"), list)
    require_type(errors, "DEMO-VALIDATION-RULES-001.json redaction", data.get("redaction"), str)
    require_type(errors, "DEMO-VALIDATION-RULES-001.json scope_note", data.get("scope_note"), str)
    require_type(errors, "DEMO-VALIDATION-RULES-001.json version", data.get("version"), str)

    if isinstance(data.get("critical_errors"), list):
        for idx, item in enumerate(data["critical_errors"]):
            if not isinstance(item, dict):
                errors.append(f"DEMO-VALIDATION-RULES-001.json critical_errors[{idx}] must be an object")
                continue
            if "id" not in item or "condition" not in item:
                errors.append(f"DEMO-VALIDATION-RULES-001.json critical_errors[{idx}] missing id or condition")


def validate_normalized_records(data, errors):
    require_type(errors, "DEMO-NORMALIZED-001.json output", data, list)
    if not isinstance(data, list):
        return
    for idx, record in enumerate(data):
        if not isinstance(record, dict):
            errors.append(f"DEMO-NORMALIZED-001.json[{idx}] must be an object")
            continue
        if "source_record_index" not in record:
            errors.append(f"DEMO-NORMALIZED-001.json[{idx}] is missing source_record_index")
        else:
            require_type(errors, f"DEMO-NORMALIZED-001.json[{idx}].source_record_index", record["source_record_index"], int)
        if "product_name" in record and not isinstance(record["product_name"], (str, type(None))):
            errors.append(f"DEMO-NORMALIZED-001.json[{idx}].product_name must be a string or null")
        if "image_filename" in record and not isinstance(record["image_filename"], (str, type(None))):
            errors.append(f"DEMO-NORMALIZED-001.json[{idx}].image_filename must be a string or null")
        if "terpenes" in record:
            require_type(errors, f"DEMO-NORMALIZED-001.json[{idx}].terpenes", record["terpenes"], dict)
        if "cannabinoids" in record:
            require_type(errors, f"DEMO-NORMALIZED-001.json[{idx}].cannabinoids", record["cannabinoids"], dict)
        for pii_field in ("customer", "customer_license"):
            if pii_field in record and record[pii_field] not in (None, "[REDACTED]"):
                errors.append(f"DEMO-NORMALIZED-001.json[{idx}].{pii_field} is not redacted")


def validate_ground_truth(data, errors):
    require_type(errors, "DEMO-GROUND-TRUTH-001.json artifact_id", data.get("artifact_id"), str)
    if data.get("artifact_id") != "DEMO-GROUND-TRUTH-001":
        errors.append("DEMO-GROUND-TRUTH-001.json artifact_id must be 'DEMO-GROUND-TRUTH-001'")

    records = data.get("records")
    require_type(errors, "DEMO-GROUND-TRUTH-001.json records", records, list)
    if isinstance(records, list):
        for idx, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"DEMO-GROUND-TRUTH-001.json records[{idx}] must be an object")
                continue
            if "source_record_index" not in record:
                errors.append(f"DEMO-GROUND-TRUTH-001.json records[{idx}] missing source_record_index")
            else:
                require_type(errors, f"DEMO-GROUND-TRUTH-001.json records[{idx}].source_record_index", record["source_record_index"], int)

    require_type(errors, "DEMO-GROUND-TRUTH-001.json version", data.get("version"), str)


def validate_benchmark_report(data, errors):
    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json artifact_id", data.get("artifact_id"), str)
    if data.get("artifact_id") != "DEMO-BENCHMARK-REPORT-001":
        errors.append("DEMO-BENCHMARK-REPORT-001.json artifact_id must be 'DEMO-BENCHMARK-REPORT-001'")

    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json accuracy", data.get("accuracy"), (int, float))
    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json numerator", data.get("numerator"), int)
    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json denominator", data.get("denominator"), int)
    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json field_results", data.get("field_results"), list)
    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json critical_errors", data.get("critical_errors"), list)
    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json scope_note", data.get("scope_note"), str)
    require_type(errors, "DEMO-BENCHMARK-REPORT-001.json version", data.get("version"), str)

    field_results = data.get("field_results")
    if isinstance(field_results, list):
        numerator = sum(1 for row in field_results if row.get("disposition") == "PASS") if field_results else 0
        denominator = len(field_results)
        if data.get("numerator") != numerator:
            errors.append(
                "DEMO-BENCHMARK-REPORT-001.json numerator must equal the number of PASS dispositions "
                f"({data.get('numerator')} != {numerator})"
            )
        if data.get("denominator") != denominator:
            errors.append(
                "DEMO-BENCHMARK-REPORT-001.json denominator must equal len(field_results) "
                f"({data.get('denominator')} != {denominator})"
            )
        if denominator:
            expected_accuracy = 100.0 * numerator / denominator
            if abs(float(data.get("accuracy", 0)) - expected_accuracy) > 1e-9:
                errors.append(
                    "DEMO-BENCHMARK-REPORT-001.json accuracy must match numerator/denominator "
                    f"({data.get('accuracy')} != {expected_accuracy})"
                )


def validate_evidence_manifest(data, errors, root: Path):
    require_type(errors, "DEMO-EVIDENCE-001.json artifact_id", data.get("artifact_id"), str)
    if data.get("artifact_id") != "DEMO-EVIDENCE-001":
        errors.append("DEMO-EVIDENCE-001.json artifact_id must be 'DEMO-EVIDENCE-001'")

    require_type(errors, "DEMO-EVIDENCE-001.json artifacts", data.get("artifacts"), list)
    require_type(errors, "DEMO-EVIDENCE-001.json hash_algorithm", data.get("hash_algorithm"), str)
    if data.get("hash_algorithm") != "SHA-256":
        errors.append("DEMO-EVIDENCE-001.json hash_algorithm must be 'SHA-256'")
    require_type(errors, "DEMO-EVIDENCE-001.json signature_status", data.get("signature_status"), str)
    require_type(errors, "DEMO-EVIDENCE-001.json version", data.get("version"), str)

    if not isinstance(data.get("artifacts"), list):
        return

    seen = {}
    for idx, entry in enumerate(data["artifacts"]):
        if not isinstance(entry, dict):
            errors.append(f"DEMO-EVIDENCE-001.json artifacts[{idx}] must be an object")
            continue
        name = entry.get("name")
        sha256 = entry.get("sha256")
        if not isinstance(name, str):
            errors.append(f"DEMO-EVIDENCE-001.json artifacts[{idx}].name must be a string")
            continue
        if name in seen:
            errors.append(f"DEMO-EVIDENCE-001.json references {name!r} more than once")
            continue
        seen[name] = True

        if not isinstance(sha256, str) or not SHA256_RE.fullmatch(sha256):
            errors.append(f"DEMO-EVIDENCE-001.json artifacts[{idx}].sha256 must be a lowercase 64-character SHA-256 hex digest")

        candidate = root / name
        if not candidate.exists() or not candidate.is_file():
            errors.append(f"DEMO-EVIDENCE-001.json references missing repository artifact: {name}")
            continue

        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if candidate.name != "DEMO-EVIDENCE-001.json" and sha256 != digest:
            errors.append(f"DEMO-EVIDENCE-001.json hash mismatch for {name}: expected {digest}, found {sha256}")

    for filename in sorted(root.iterdir()):
        if filename.is_file() and filename.name.endswith(".json"):
            if filename.name not in seen and filename.name == "DEMO-EVIDENCE-001.json":
                continue
            if filename.name not in seen and filename.name not in {"DEMO-EVIDENCE-001.json"}:
                continue
    if len(seen) != len(data["artifacts"]):
        errors.append("DEMO-EVIDENCE-001.json artifacts are duplicated")


def validate_independent_verification(data, errors):
    require_type(errors, "DEMO-INDEPENDENT-VERIFICATION-001.json artifact_id", data.get("artifact_id"), str)
    if data.get("artifact_id") != "DEMO-INDEPENDENT-VERIFICATION-001":
        errors.append("DEMO-INDEPENDENT-VERIFICATION-001.json artifact_id must be 'DEMO-INDEPENDENT-VERIFICATION-001'")

    status = data.get("status")
    require_type(errors, "DEMO-INDEPENDENT-VERIFICATION-001.json status", status, str)
    if status not in {"PASS", "FAIL"}:
        errors.append("DEMO-INDEPENDENT-VERIFICATION-001.json status must be 'PASS' or 'FAIL'")

    require_type(errors, "DEMO-INDEPENDENT-VERIFICATION-001.json failures", data.get("failures"), list)
    if isinstance(data.get("failures"), list) and status == "PASS" and data["failures"]:
        errors.append("DEMO-INDEPENDENT-VERIFICATION-001.json PASS report must have an empty failures list")

    require_type(errors, "DEMO-INDEPENDENT-VERIFICATION-001.json manifest_signature_status", data.get("manifest_signature_status"), str)
    require_type(errors, "DEMO-INDEPENDENT-VERIFICATION-001.json note", data.get("note"), str)


def validate_repository(root: Path):
    errors = []

    try:
        dataset = load_json(REQUIRED_FILES["dataset"])
        taxonomy = load_json(REQUIRED_FILES["taxonomy"])
        validation_rules = load_json(REQUIRED_FILES["validation_rules"])
        normalized = load_json(REQUIRED_FILES["normalized"])
        ground_truth = load_json(REQUIRED_FILES["ground_truth"])
        benchmark = load_json(REQUIRED_FILES["benchmark"])
        evidence = load_json(REQUIRED_FILES["evidence"])
        independent_verification = load_json(REQUIRED_FILES["independent_verification"])
    except (FileNotFoundError, ValueError) as exc:
        return [str(exc)]

    validate_dataset(dataset, errors)
    validate_taxonomy(taxonomy, errors)
    validate_validation_rules(validation_rules, errors)
    validate_normalized_records(normalized, errors)
    validate_ground_truth(ground_truth, errors)
    validate_benchmark_report(benchmark, errors)
    validate_evidence_manifest(evidence, errors, root)
    validate_independent_verification(independent_verification, errors)

    if isinstance(normalized, list) and isinstance(ground_truth.get("records"), list):
        if len(normalized) != len(ground_truth["records"]):
            errors.append(
                "DEMO-NORMALIZED-001.json must contain the same number of records as DEMO-GROUND-TRUTH-001.json "
                f"({len(normalized)} != {len(ground_truth['records'])})"
            )

    return errors


def main():
    errors = validate_repository(ROOT)
    if errors:
        print("Artifact validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("OK: all repository JSON artifacts are valid and internally consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
