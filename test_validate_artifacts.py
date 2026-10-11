import json
import shutil
from pathlib import Path

import validate_artifacts as va

ROOT = Path(__file__).resolve().parent
REQUIRED_FILES = [
    "DEMO-DATASET-001.json",
    "DEMO-TAXONOMY-001.json",
    "DEMO-VALIDATION-RULES-001.json",
    "DEMO-NORMALIZED-001.json",
    "DEMO-GROUND-TRUTH-001.json",
    "DEMO-BENCHMARK-REPORT-001.json",
    "DEMO-EVIDENCE-001.json",
    "DEMO-INDEPENDENT-VERIFICATION-001.json",
    "benchmark_runner.py",
    "verify_poc.py",
]


def copy_required_files(target_dir):
    for name in REQUIRED_FILES:
        shutil.copy2(ROOT / name, target_dir / name)


def test_validate_repository_reports_malformed_dataset_contract(tmp_path):
    copy_required_files(tmp_path)

    dataset = json.loads((tmp_path / "DEMO-DATASET-001.json").read_text(encoding="utf-8"))
    dataset["artifact_id"] = "WRONG-ID"
    dataset["record_count"] = 999
    (tmp_path / "DEMO-DATASET-001.json").write_text(json.dumps(dataset, separators=(",", ":")), encoding="utf-8")

    errors = va.validate_repository(tmp_path)

    assert any("artifact_id must be 'DEMO-DATASET-001'" in error for error in errors)
    assert any("record_count must equal len(records)" in error for error in errors)


def test_validate_repository_reports_invalid_evidence_references(tmp_path):
    copy_required_files(tmp_path)

    evidence = json.loads((tmp_path / "DEMO-EVIDENCE-001.json").read_text(encoding="utf-8"))
    evidence["artifacts"] = [
        {"name": "DEMO-NORMALIZED-001.json", "sha256": "0" * 64},
        {"name": "DEMO-NORMALIZED-001.json", "sha256": "1" * 64},
        {"name": "MISSING-ARTIFACT.json", "sha256": "2" * 64},
    ]
    (tmp_path / "DEMO-EVIDENCE-001.json").write_text(json.dumps(evidence, separators=(",", ":")), encoding="utf-8")

    errors = va.validate_repository(tmp_path)

    assert any("more than once" in error for error in errors)
    assert any("MISSING-ARTIFACT.json" in error for error in errors)
    assert any("sha256 must be a lowercase" in error for error in errors)
