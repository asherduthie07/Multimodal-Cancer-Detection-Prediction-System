import hashlib
from packages.contracts.schemas import Case, Prediction, DataMode
from ml.alignment.core import align_case
from ml.tasks.registry import TASKS


def predict(case: Case, task_id: str) -> Prediction:
    task = TASKS.get(task_id)
    if task is None:
        raise ValueError("Unknown task")
    reasons: list[str] = []
    if case.cancer_type != task.cancer_type:
        reasons.append("Unsupported cancer type for task")
    if task.evaluation_status == "unavailable":
        reasons.append("No evaluated model for this endpoint")
    report = align_case(case, task)
    for required in task.required_modalities:
        if required not in report.accepted_modalities:
            reasons.append(f"Missing accepted required modality: {required}")
    if case.mode != DataMode.synthetic_demo:
        reasons.append("No trained and evaluated real-data model is configured")
    if reasons:
        return Prediction(case_id=case.id, task_id=task_id, endpoint=task.endpoint,
            mode=case.mode, model_version=None, evaluation_status="unavailable",
            status="abstained", abstention_reasons=reasons,
            explanation="No research prediction is available for these inputs.")
    # Deterministic UI exercise only. This is never exposed as a fitted probability.
    digest = hashlib.sha256(case.id.encode()).digest()
    fixture = 0.25 + (digest[0] / 255) * 0.5
    return Prediction(case_id=case.id, task_id=task_id, endpoint=task.endpoint,
        mode=case.mode, model_version="synthetic-fixture-v1", evaluation_status="synthetic_demo",
        modalities_used=report.accepted_modalities, status="prediction", probability=round(fixture, 3),
        risk_group="Synthetic demonstration group",
        explanation="Deterministic synthetic fixture for testing workflow only; not a trained model or clinical risk estimate.")
