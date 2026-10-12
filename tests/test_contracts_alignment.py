from datetime import timedelta

from ml.alignment.core import align_case
from ml.fusion.contracts import check_feature_compatibility
from ml.fusion.inference import predict
from ml.tasks.registry import TASKS
from packages.contracts.schemas import DataMode, FeatureArtifact, ModelVersion
from services.api.oncofusion.demo import make_demo_case
from services.api.oncofusion.validation import validate_case


TASK = TASKS["breast_mammo_detection_demo"]


def test_demo_alignment_and_synthetic_label():
    case = make_demo_case()
    report = align_case(case, TASK)
    assert report.valid
    assert report.accepted_modalities == ["clinical", "genomics", "imaging"]
    result = predict(case, TASK.id)
    assert result.status == "prediction"
    assert result.mode == DataMode.synthetic_demo
    assert result.evaluation_status == "synthetic_demo"
    assert "not a trained model" in result.explanation


def test_patient_and_result_time_leakage_excluded():
    case = make_demo_case()
    case.imaging[0].case_id = "OTHER-PATIENT"
    case.assays[0].available_at = case.index_time + timedelta(days=1)
    report = align_case(case, TASK)
    assert {item.status for item in report.items if item.modality != "clinical"} == {"unmatched", "excluded"}
    assert not report.valid
    assert predict(case, TASK.id).status == "abstained"


def test_split_and_failed_qc_excluded():
    case = make_demo_case()
    case.split = "test"
    case.imaging[0].split = "train"
    case.assays[0].qc_passed = False
    case.assays[0].qc_reasons = ["synthetic QC failure"]
    report = align_case(case, TASK)
    assert any("different patient partition" in item.reason for item in report.items)
    assert any("Failed quality control" in item.reason for item in report.items)
    assert not report.valid


def test_assay_specimen_source_must_match():
    case = make_demo_case()
    case.assays[0].subtype = "tissue_expression"
    assert any("requires tissue specimen" in item for item in validate_case(case))


def test_real_mode_abstains_without_evaluated_model():
    case = make_demo_case()
    case.mode = DataMode.real_research
    case.dataset_id = "audited-external"
    result = predict(case, TASK.id)
    assert result.status == "abstained"
    assert result.probability is None


def test_feature_schema_and_dimension_contracts():
    model = ModelVersion(id="m1", task_id=TASK.id, supported_modalities=["clinical"],
        supported_subtypes={"clinical": ["structured"]}, feature_schema_versions={"clinical": "v1"},
        feature_dimensions={"clinical": 128}, evaluation_status="unavailable")
    feature = FeatureArtifact(id="f1", case_id="P1", modality="clinical", subtype="structured",
        embedding_uri="artifact://f1", dimensions=64, encoder_version="e1", preprocessing_version="p1",
        feature_schema_version="v2", available=True, source_ids=["s1"])
    errors = check_feature_compatibility([feature], model)
    assert "Feature schema mismatch for clinical" in errors
    assert "Feature dimension mismatch for clinical" in errors
