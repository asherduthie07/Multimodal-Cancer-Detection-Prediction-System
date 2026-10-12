from datetime import datetime, timezone, timedelta
from packages.contracts.schemas import Case, ClinicalObservation, DataMode, ImagingStudy, LaboratoryAssay, Specimen


def make_demo_case() -> Case:
    index = datetime(2025, 1, 15, 10, tzinfo=timezone.utc)
    earlier = index - timedelta(days=3)
    common = dict(case_id="DEMO-001", dataset_id="oncofusion-synthetic-v1", acquired_at=earlier, available_at=earlier)
    return Case(id="DEMO-001", dataset_id="oncofusion-synthetic-v1", cancer_type="breast",
        mode=DataMode.synthetic_demo, index_time=index,
        specimens=[Specimen(id="SPEC-001", source_id="synthetic-specimen", source="blood", **common)],
        imaging=[ImagingStudy(id="IMG-001", source_id="synthetic-image", subtype="mammography",
            view="CC", laterality="L", burned_in_identifier_reviewed=True, **common)],
        assays=[LaboratoryAssay(id="ASSAY-001", source_id="synthetic-assay", specimen_id="SPEC-001",
            subtype="protein_biomarker", assay_id="synthetic-panel", assay_version="1",
            feature_schema_version="demo-1", units="arbitrary synthetic units", reference_convention="synthetic",
            features={"marker_a": 0.4, "marker_b": 0.7}, **common)],
        clinical=[ClinicalObservation(id="CLIN-001", source_id="synthetic-observation", code="age",
            value=54, unit="years", category="demographics", **common)])
