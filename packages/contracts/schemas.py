from __future__ import annotations

from datetime import datetime
from enum import Enum
import re
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


class DataMode(str, Enum):
    synthetic_demo = "synthetic_demo"
    real_research = "real_research"


class EvidenceBase(BaseModel):
    id: str
    case_id: str
    dataset_id: str
    source_id: str
    acquired_at: datetime
    available_at: datetime
    file_sha256: str | None = None
    artifact_uri: str | None = None
    qc_passed: bool = True
    qc_reasons: list[str] = Field(default_factory=list)
    split: Literal["train", "validation", "test"] | None = None


class Encounter(BaseModel):
    id: str
    case_id: str
    occurred_at: datetime
    kind: str


class Specimen(EvidenceBase):
    encounter_id: str | None = None
    source: Literal["tissue", "blood"]
    anatomical_site: str | None = None


class ImagingStudy(EvidenceBase):
    encounter_id: str | None = None
    subtype: Literal["mammography", "ct", "mri", "pathology"]
    view: str | None = None
    laterality: Literal["L", "R", "B"] | None = None
    pixel_spacing_mm: tuple[float, float] | None = None
    burned_in_identifier_reviewed: bool = False


class LaboratoryAssay(EvidenceBase):
    specimen_id: str
    subtype: Literal["tissue_expression", "tissue_mutation", "blood_ctdna", "blood_methylation", "blood_fragmentomics", "protein_biomarker"]
    assay_id: str
    assay_version: str
    feature_schema_version: str
    units: str
    reference_convention: str
    detection_limit: float | None = None
    features: dict[str, float | None] = Field(default_factory=dict)


class ClinicalObservation(EvidenceBase):
    encounter_id: str | None = None
    code: str
    value: float | str | bool | None
    unit: str | None = None
    category: str


class Case(BaseModel):
    id: str
    dataset_id: str
    cancer_type: str
    mode: DataMode
    index_time: datetime
    split: Literal["train", "validation", "test"] | None = None
    encounters: list[Encounter] = Field(default_factory=list)
    specimens: list[Specimen] = Field(default_factory=list)
    imaging: list[ImagingStudy] = Field(default_factory=list)
    assays: list[LaboratoryAssay] = Field(default_factory=list)
    clinical: list[ClinicalObservation] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def safe_case_id(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
            raise ValueError("Case ID may contain only letters, numbers, hyphens, and underscores")
        return value


class DatasetManifest(BaseModel):
    id: str
    source_name: str
    mode: DataMode
    cancer_type: str
    task_id: str
    patient_count: int
    estimated_bytes: int
    sha256: str
    reuse_permission: str
    records_uri: str


class FeatureArtifact(BaseModel):
    id: str
    case_id: str
    specimen_id: str | None = None
    modality: Literal["imaging", "genomics", "clinical"]
    subtype: str
    embedding_uri: str
    dimensions: int = Field(gt=0)
    encoder_version: str
    preprocessing_version: str
    feature_schema_version: str
    available: bool
    quality: dict[str, Any] = Field(default_factory=dict)
    source_ids: list[str]
    source_hashes: list[str] = Field(default_factory=list)


class ModelVersion(BaseModel):
    id: str
    task_id: str
    supported_modalities: list[str]
    supported_subtypes: dict[str, list[str]]
    feature_schema_versions: dict[str, str]
    feature_dimensions: dict[str, int] = Field(default_factory=dict)
    evaluation_status: Literal["unavailable", "synthetic_demo", "internally_evaluated", "externally_validated"]
    calibration_version: str | None = None
    artifact_uri: str | None = None


class AlignmentItem(BaseModel):
    source_id: str
    modality: str
    status: Literal["accepted", "excluded", "unmatched"]
    reason: str


class AlignmentReport(BaseModel):
    case_id: str
    task_id: str
    index_time: datetime
    items: list[AlignmentItem]
    accepted_modalities: list[str]
    valid: bool


class Prediction(BaseModel):
    case_id: str
    task_id: str
    endpoint: str
    mode: DataMode
    model_version: str | None
    evaluation_status: str
    modalities_used: list[str] = Field(default_factory=list)
    status: Literal["prediction", "abstained"]
    probability: float | None = None
    risk_group: str | None = None
    abstention_reasons: list[str] = Field(default_factory=list)
    explanation: str


class InferenceJob(BaseModel):
    id: str
    case_id: str
    task_id: str
    status: Literal["queued", "running", "completed", "failed"]
    error: str | None = None
    prediction: Prediction | None = None


class ExpertReview(BaseModel):
    id: str
    case_id: str
    prediction_job_id: str
    reviewer_id: str
    created_at: datetime
    assessment: str
    notes: str | None = None
