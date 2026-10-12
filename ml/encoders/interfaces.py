from typing import Protocol
from packages.contracts.schemas import Case, FeatureArtifact


class Encoder(Protocol):
    modality: str
    subtype: str

    def extract(self, case: Case) -> FeatureArtifact: ...


class UnavailableEncoderError(RuntimeError):
    pass


class MammographyEncoder:
    modality = "imaging"
    subtype = "mammography"

    def extract(self, case: Case) -> FeatureArtifact:
        raise UnavailableEncoderError("No trusted pretrained mammography weights are configured")


class MolecularEncoder:
    modality = "genomics"
    subtype = "protein_biomarker"

    def extract(self, case: Case) -> FeatureArtifact:
        raise UnavailableEncoderError("No fitted assay-specific preprocessing and model are configured")


class ClinicalEncoder:
    modality = "clinical"
    subtype = "structured"

    def extract(self, case: Case) -> FeatureArtifact:
        raise UnavailableEncoderError("No fitted clinical preprocessing and model are configured")
