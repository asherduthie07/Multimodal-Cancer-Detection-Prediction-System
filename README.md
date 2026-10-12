# OncoFusion

OncoFusion is a research prototype for reviewing patient-matched imaging, molecular, and structured clinical evidence. **It is not a clinically validated diagnostic device.** The bundled case and numeric output are synthetic software fixtures; no real patient data, fitted weights, or performance claims are included.

## Run locally

Prerequisites: Python 3.11 or 3.13, Node 22.12 or newer, npm, and optionally Docker Compose.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHONPATH=. .venv/bin/uvicorn services.api.oncofusion.main:app --reload --port 8000
```

In a second terminal:

```bash
cd apps/web
npm ci
npm start
```

Open `http://localhost:4200`, select **Create demo case**, and run research inference. Local mode uses SQLite and FastAPI background tasks. For PostgreSQL, Redis, and a separate worker:

```bash
cp .env.example .env
docker compose up --build
```

The Compose setup serves the same UI on port 4200 and API on port 8000. Docker was unavailable in the authoring environment, so Compose startup has not been executed here.

## Tests

```bash
.venv/bin/pytest -q
cd apps/web && npm run build
```

## API

The OpenAPI explorer is at `http://localhost:8000/docs`. Key operations: `POST /demo/case`, `POST /cases`, `GET /cases`, `GET /cases/{id}`, `POST /cases/{id}/validate`, `POST /cases/{id}/align/{task_id}`, `POST /cases/{id}/assets`, `POST /cases/{id}/inference/{task_id}`, `GET /jobs/{id}`, `GET /jobs/{id}/result`, `GET /models`, and `GET /evaluations/{task_id}`.

Uploads are stored by hash outside the database and remain **unvalidated**. A successful upload does not enroll evidence for inference. Raw DICOM, PNG, JPEG, CSV, TSV, and Parquet filenames are accepted within a 25 MB local limit; only PNG signatures and standard DICOM preambles receive an initial content check. Deidentification and burned-in identifier review remain mandatory before real use.

## Scientific boundaries

- The available demo endpoint is **study malignancy classification for synthetic breast mammography** at examination time. Its score is deterministic and is not a fitted probability.
- Future incidence is listed in the task registry but unavailable. Prognosis is not relabeled as future detection.
- Real-data requests abstain. CT, MRI, pathology, tissue RNA, ctDNA, methylation, and fragmentomics contracts are present, but no usable encoder weights or evaluated models are bundled.
- Clinical result availability, acquisition time, patient identity, specimen association, subtype, QC, and split compatibility are checked before alignment.

See [implementation status](IMPLEMENTATION_STATUS.md), [architecture](docs/ARCHITECTURE.md), [dataset onboarding](docs/DATASETS.md), and [model card](docs/MODEL_CARD.md).
