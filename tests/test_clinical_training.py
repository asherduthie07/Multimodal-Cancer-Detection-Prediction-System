import csv
import json

from ml.evaluation.train_clinical import run


def test_clinical_baseline_runs_on_explicit_synthetic_splits(tmp_path):
    data = tmp_path / "synthetic_clinical.csv"
    split = tmp_path / "split.json"
    columns = ["patient_id", "label", "index_time", "available_at", "age", "history"]
    with data.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for i in range(30):
            writer.writerow(dict(patient_id=f"SYN-{i:02}", label=str(i % 2),
                index_time="2025-01-02", available_at="2025-01-01",
                age=str(40 + i), history="yes" if i % 3 else "no"))
    assignments = {f"SYN-{i:02}": "train" if i < 20 else "validation" if i < 25 else "test"
                   for i in range(30)}
    split.write_text(json.dumps({"patient_assignments": assignments}))
    result = run(data, split, ["age"], ["history"])
    assert result["validation"]["n"] == 5
    assert result["test"]["n"] == 5
    assert result["status"] == "synthetic_test_only"
    assert result["threshold_policy"].startswith("prespecified")


def test_clinical_baseline_rejects_post_index_evidence(tmp_path):
    data = tmp_path / "synthetic_clinical.csv"
    data.write_text("patient_id,label,index_time,available_at,age\nP1,1,2025-01-01,2025-01-02,50\n")
    split = tmp_path / "split.json"
    split.write_text(json.dumps({"patient_assignments": {"P1": "train"}}))
    try:
        run(data, split, ["age"], [])
    except ValueError as exc:
        assert "unavailable at index" in str(exc)
    else:
        raise AssertionError("Expected temporal leakage rejection")
