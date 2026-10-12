from packages.contracts.schemas import Case


def validate_case(case: Case) -> list[str]:
    issues: list[str] = []
    if case.mode.value == "real_research" and case.dataset_id.startswith("oncofusion-synthetic"):
        issues.append("Synthetic dataset cannot be labeled real research")
    for assay in case.assays:
        specimen = next((s for s in case.specimens if s.id == assay.specimen_id), None)
        if specimen is None:
            issues.append(f"Assay {assay.id} has no matching specimen")
        elif assay.subtype.startswith("tissue_") and specimen.source != "tissue":
            issues.append(f"Assay {assay.id} requires tissue specimen")
        elif assay.subtype.startswith("blood_") and specimen.source != "blood":
            issues.append(f"Assay {assay.id} requires blood specimen")
        if not assay.units or not assay.assay_version or not assay.feature_schema_version:
            issues.append(f"Assay {assay.id} lacks required unit or version metadata")
    return issues
