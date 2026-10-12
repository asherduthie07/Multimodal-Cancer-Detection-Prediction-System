# Implementation status

Updated 2026-10-12. Status describes executed work, not intended features.

| Component | Status | Evidence / limitation |
| --- | --- | --- |
| Typed case, evidence, feature, model, job, prediction contracts | Implemented and tested | Pydantic validation and contract tests |
| Three modality interfaces and subtype registry | Implemented but not trained | Mammography, molecular, clinical encoders explicitly report unavailable weights |
| Synthetic case, alignment, API, asynchronous job, result | Implemented and tested | API flow test; deterministic fixture clearly labeled |
| PostgreSQL, Redis worker, local artifacts, S3 adapter | Implemented but not integration tested | Compose provided; Docker unavailable locally; S3 adapter requires optional boto3 |
| Angular evidence dashboard | Implemented; build verification pending | Displays case, three pipelines, alignment, result, evaluation status |
| Bounded manifest audit and immutable patient split output | Implemented and tested | Does not ingest a real cohort |
| Real cohort adapter and clinical-only fitted baseline | Planned or blocked | Requires source audit, reuse permission, label definition, and data |
| Image preprocessing and pretrained embeddings | Planned or blocked | No trusted weights or image dataset configured |
| Molecular preprocessing, fitted encoders, cached embeddings | Planned or blocked | No compatible assay dataset configured |
| Concatenation, learned fusion, contrastive alignment | Planned or blocked | Requires genuine matched patient training data |
| Calibration, risk thresholds, detection metrics, survival evaluation | Planned or blocked | No trained real model or labels |
| Internal evaluation | None | Zero real patients evaluated |
| External validation | None | Zero external cohorts evaluated |

Actual automated result: backend/model-contract tests **9 passed** with one third-party deprecation warning. No model training or clinical validation was run.
