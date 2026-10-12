import csv
from ml.data.audit import audit_manifest, patient_split


def test_patient_split_keeps_repeated_records_together(tmp_path):
    path = tmp_path / "manifest.csv"
    columns = ["patient_id", "source_id", "cancer_type", "modality", "subtype", "available_at", "index_time"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for patient in range(20):
            for specimen in range(2):
                writer.writerow(dict(patient_id=f"P{patient}", source_id=f"S{patient}-{specimen}",
                    cancer_type="breast", modality="clinical", subtype="structured",
                    available_at="2025-01-01", index_time="2025-01-02"))
    audit = audit_manifest(path)
    split = patient_split(audit)
    assert audit["records"] == 40
    assert audit["patients"] == 20
    assert len(split["patient_assignments"]) == 20
    assert split == patient_split(audit)
