"""Run an audited clinical-only baseline. No model is registered automatically."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from ml.evaluation.detection import detection_metrics
from ml.preprocessing.clinical import clinical_baseline


def run(data_path: Path, split_path: Path, numeric: list[str], categorical: list[str],
        source_manifest: Path | None = None) -> dict:
    raw = data_path.read_bytes()
    data_sha256 = hashlib.sha256(raw).hexdigest()
    mode = "synthetic_test_only"
    if source_manifest:
        source = json.loads(source_manifest.read_text())
        if source.get("mode") != "real_research" or source.get("sha256") != data_sha256:
            raise ValueError("Real source manifest mode or hash mismatch")
        if not source.get("reuse_permission") or not source.get("label_definition"):
            raise ValueError("Real source manifest lacks permission or label definition")
        mode = "real_research"
    with data_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    split = json.loads(split_path.read_text())
    if not rows or any(not row.get("patient_id") for row in rows):
        raise ValueError("Every row needs a patient_id")
    assignments = split["patient_assignments"]
    if set(row["patient_id"] for row in rows) - set(assignments):
        raise ValueError("Unassigned patients in data")
    if len(rows) != len({row["patient_id"] for row in rows}):
        raise ValueError("Baseline expects one index-time row per patient")
    if any(row.get("available_at", "") > row.get("index_time", "") for row in rows):
        raise ValueError("Rows contain evidence unavailable at index time")
    features = numeric + categorical
    if any(any(name not in row for name in features + ["label"]) for row in rows):
        raise ValueError("Missing feature or label column")
    if any(row["label"] not in {"0", "1"} for row in rows):
        raise ValueError("Binary labels must be 0 or 1")
    partitions = {name: [row for row in rows if assignments[row["patient_id"]] == name]
                  for name in ("train", "validation", "test")}
    if not partitions["train"] or not partitions["validation"] or not partitions["test"]:
        raise ValueError("Train, validation, and test patients are required")
    def x(part):
        return [[float(row[name]) if row[name] else float("nan") for name in numeric] +
                [row[name] if row[name] else float("nan") for name in categorical]
                for row in partitions[part]]
    def y(part):
        return [int(row["label"]) for row in partitions[part]]
    model = clinical_baseline(numeric, categorical)
    model.fit(x("train"), y("train"))
    # Pick a development operating point, then use it unchanged for final test.
    validation_prob = model.predict_proba(x("validation"))[:, 1]
    threshold = 0.5
    validation = detection_metrics(y("validation"), validation_prob, threshold)
    test = detection_metrics(y("test"), model.predict_proba(x("test"))[:, 1], threshold)
    return {"status": "internally_evaluated" if mode == "real_research" else "synthetic_test_only",
            "mode": mode, "data_sha256": data_sha256,
            "split_sha256": hashlib.sha256(split_path.read_bytes()).hexdigest(),
            "numeric_features": numeric, "categorical_features": categorical,
            "threshold_policy": "prespecified 0.5 development operating point", "validation": validation, "test": test,
            "limitations": "Internal patient split only; no calibration, confidence intervals, or external validation."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("split", type=Path)
    parser.add_argument("--numeric", nargs="*", default=[])
    parser.add_argument("--categorical", nargs="*", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Evaluation report already exists")
    args.output.write_text(json.dumps(run(args.data, args.split, args.numeric, args.categorical,
                                           args.source_manifest), indent=2))


if __name__ == "__main__":
    main()
