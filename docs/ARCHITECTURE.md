# Architecture

The Angular client reads task, case, alignment, job, and evaluation state from FastAPI. FastAPI persists JSON-backed case and job records in SQLite for local development or PostgreSQL in Compose. Uploaded bytes live in a content-addressed local artifact store; an S3-compatible adapter is defined for later deployment. Redis queues jobs to a separate Python worker in Compose. Local mode uses FastAPI background tasks.

The shared Pydantic contracts cover cases, encounters, specimens, studies, assays, observations, manifests, features, model versions, predictions, and expert reviews. Every evidence item carries source and dataset IDs, acquisition and result-availability times, QC state, and optional split membership. The alignment layer reports accepted, excluded, and unmatched inputs. It checks case identity, task subtype, specimen linkage, QC, acquisition time, result-availability time, and partition compatibility.

The task registry currently permits only synthetic mammography detection. Future incidence is represented as unavailable. The three encoder interfaces intentionally raise explicit unavailable errors without trusted fitted artifacts. The demo inference function emits a deterministic fixture score and labels it as synthetic; real-data mode abstains. The numeric fixture is never used for research metrics.

Before enabling real-data fusion: implement study/view grouping and image QC; assay-specific unit and schema validation; clinical unit normalization and train-only preprocessing; actual feature artifacts with trusted hashes; patient-matched training; task-specific calibration; held-out evaluation; and versioned thresholds. Learned fusion should be compared with unimodal and concatenation baselines on the same patient subset.
