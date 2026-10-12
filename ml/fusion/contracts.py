from packages.contracts.schemas import FeatureArtifact, ModelVersion


def check_feature_compatibility(features: list[FeatureArtifact], model: ModelVersion) -> list[str]:
    errors: list[str] = []
    if len({feature.case_id for feature in features}) > 1:
        errors.append("Feature artifacts belong to different cases")
    for feature in features:
        if feature.modality not in model.supported_modalities:
            errors.append(f"Unsupported modality: {feature.modality}")
        if feature.subtype not in model.supported_subtypes.get(feature.modality, []):
            errors.append(f"Unsupported subtype: {feature.subtype}")
        expected_schema = model.feature_schema_versions.get(feature.modality)
        if expected_schema != feature.feature_schema_version:
            errors.append(f"Feature schema mismatch for {feature.modality}")
        expected_dimensions = model.feature_dimensions.get(feature.modality)
        if expected_dimensions is not None and expected_dimensions != feature.dimensions:
            errors.append(f"Feature dimension mismatch for {feature.modality}")
        if not feature.available:
            errors.append(f"Feature unavailable: {feature.id}")
    return errors
