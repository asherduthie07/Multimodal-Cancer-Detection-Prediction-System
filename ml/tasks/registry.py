from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    id: str
    cancer_type: str
    population: str
    endpoint: str
    label_definition: str
    index_definition: str
    required_modalities: tuple[str, ...]
    optional_modalities: tuple[str, ...]
    supported_subtypes: dict[str, tuple[str, ...]]
    horizon_days: int | None
    evaluation_status: str


TASKS = {
    "breast_mammo_detection_demo": Task(
        id="breast_mammo_detection_demo", cancer_type="breast",
        population="Synthetic mammography examinations only",
        endpoint="Study malignancy classification",
        label_definition="Synthetic binary fixture label; no clinical ground truth",
        index_definition="Mammography examination time",
        required_modalities=("imaging",), optional_modalities=("genomics", "clinical"),
        supported_subtypes={"imaging": ("mammography",), "genomics": ("protein_biomarker",), "clinical": ("structured",)},
        horizon_days=None, evaluation_status="synthetic_demo",
    ),
    "breast_future_incidence": Task(
        id="breast_future_incidence", cancer_type="breast",
        population="Requires an audited longitudinal cohort",
        endpoint="Future breast cancer incidence",
        label_definition="Cancer diagnosis during a prespecified future interval",
        index_definition="Pre-diagnosis screening date",
        required_modalities=(), optional_modalities=(), supported_subtypes={},
        horizon_days=365, evaluation_status="unavailable",
    ),
}
