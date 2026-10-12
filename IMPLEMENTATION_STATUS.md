# Implementation status

Updated 2026-10-12. Status describes executed work, not intended features.

| Component | Status | Evidence / limitation |
| --- | --- | --- |
| Typed case, evidence, feature, model, job, prediction contracts | Implemented and tested | Pydantic validation and contract tests |
| Three modality interfaces and subtype registry | Implemented but not trained | Mammography, molecular, clinical encoders explicitly report unavailable weights |
| Synthetic case, alignment, API, asynchronous job, result | Implemented and tested | API flow test; deterministic fixture clearly labeled |
| PostgreSQL, Redis worker, local artifacts, S3 adapter | Implemented but not integration tested | Compose provided; Docker unavailable locally; S3 adapter requires optional boto3 |
| Angular evidence dashboard | Implemented and tested | Production build and Playwright case-to-result flow passed |
| Bounded manifest audit and immutable patient split output | Implemented and tested | Does not ingest a real cohort |
| Clinical-only baseline and detection evaluation workflow | Implemented but not trained on real data | Train-only preprocessing, explicit patient split, synthetic workflow test |
| Real cohort adapter and audited experiment | Planned or blocked | Requires source audit, reuse permission, label definition, and data |
| Image preprocessing and pretrained embeddings | Planned or blocked | No trusted weights or image dataset configured |
| Molecular preprocessing, fitted encoders, cached embeddings | Planned or blocked | No compatible assay dataset configured |
| Concatenation, learned fusion, contrastive alignment | Planned or blocked | Requires genuine matched patient training data |
| Calibration, risk thresholds, detection metrics, survival evaluation | Planned or blocked | No trained real model or labels |
| Internal evaluation | None | Zero real patients evaluated |
| External validation | None | Zero external cohorts evaluated |

Actual automated result: backend/model-contract tests **11 passed** with two third-party warnings; Playwright browser flow **1 passed**; Angular production build passed. Production npm audit reported **0 vulnerabilities**; the full tree still reports **3 development dependency advisories**. Docker Compose was not run because Docker is unavailable here. The clinical workflow ran only on synthetic test rows; no real-data model training or clinical validation was run.
