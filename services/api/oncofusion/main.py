from __future__ import annotations

import hashlib
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from packages.contracts.schemas import Case, InferenceJob
from ml.alignment.core import align_case
from ml.fusion.inference import predict
from ml.tasks.registry import TASKS
from .db import CaseRecord, JobRecord, SessionLocal, init_db
from .demo import make_demo_case
from .validation import validate_case


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="OncoFusion research API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("WEB_ORIGIN", "http://localhost:4200").split(","),
    allow_methods=["GET", "POST"], allow_headers=["*"], allow_credentials=False)


def get_case(case_id: str, db: Session) -> Case:
    row = db.get(CaseRecord, case_id)
    if row is None:
        raise HTTPException(404, "Case not found")
    return Case.model_validate(row.payload)


@app.get("/health")
def health():
    return {"status": "ok", "product": "OncoFusion", "clinical_validation": False}


@app.get("/models")
def models():
    return [dict(task.__dict__) for task in TASKS.values()]


@app.get("/evaluations/{task_id}")
def evaluation(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(404, "Unknown task")
    return {"task_id": task_id, "status": TASKS[task_id].evaluation_status,
        "sample_count": 0, "metrics": {}, "message": "No real-data model evaluation has been executed."}


@app.post("/demo/case", response_model=Case)
def create_demo_case():
    case = make_demo_case()
    with SessionLocal() as db:
        db.merge(CaseRecord(id=case.id, payload=case.model_dump(mode="json")))
        db.commit()
    return case


@app.post("/cases", response_model=Case)
def create_case(case: Case):
    issues = validate_case(case)
    if issues:
        raise HTTPException(422, issues)
    with SessionLocal() as db:
        if db.get(CaseRecord, case.id):
            raise HTTPException(409, "Case already exists")
        db.add(CaseRecord(id=case.id, payload=case.model_dump(mode="json")))
        db.commit()
    return case


@app.get("/cases", response_model=list[Case])
def list_cases():
    with SessionLocal() as db:
        return [Case.model_validate(x.payload) for x in db.query(CaseRecord).all()]


@app.get("/cases/{case_id}", response_model=Case)
def case_detail(case_id: str):
    with SessionLocal() as db:
        return get_case(case_id, db)


@app.post("/cases/{case_id}/validate")
def validate(case_id: str):
    with SessionLocal() as db:
        case = get_case(case_id, db)
    issues = validate_case(case)
    return {"valid": not issues, "issues": issues, "mode": case.mode}


@app.post("/cases/{case_id}/align/{task_id}")
def align(case_id: str, task_id: str):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(404, "Unknown task")
    with SessionLocal() as db:
        case = get_case(case_id, db)
    return align_case(case, task)


@app.post("/cases/{case_id}/assets")
async def upload_asset(case_id: str, file: UploadFile = File(...)):
    with SessionLocal() as db:
        get_case(case_id, db)
    allowed = {".png", ".jpg", ".jpeg", ".dcm", ".csv", ".tsv", ".parquet"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(415, "Unsupported file type")
    max_bytes = 25 * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(413, "File exceeds 25 MB local upload limit")
    if suffix == ".png" and not content.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HTTPException(422, "Invalid PNG signature")
    if suffix == ".dcm" and (len(content) < 132 or content[128:132] != b"DICM"):
        raise HTTPException(422, "DICOM preamble is missing; manual review required")
    digest = hashlib.sha256(content).hexdigest()
    root = Path(os.getenv("ARTIFACT_DIR", "./artifacts")).resolve()
    target_dir = root / case_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{digest}{suffix}"
    target.write_bytes(content)
    return {"sha256": digest, "artifact_uri": str(target), "size": len(content),
        "registration_status": "stored_unvalidated", "message": "Upload requires metadata registration and deidentification review before model use."}


def run_job(job_id: str):
    with SessionLocal() as db:
        row = db.get(JobRecord, job_id)
        job = InferenceJob.model_validate(row.payload)
        job.status = "running"
        row.payload = job.model_dump(mode="json")
        db.commit()
        try:
            case = get_case(job.case_id, db)
            job.prediction = predict(case, job.task_id)
            job.status = "completed"
        except Exception:
            job.status = "failed"
            job.error = "Inference failed; inspect server logs without patient payloads"
        row.payload = job.model_dump(mode="json")
        db.commit()


@app.post("/cases/{case_id}/inference/{task_id}", response_model=InferenceJob, status_code=202)
def submit_inference(case_id: str, task_id: str, background: BackgroundTasks):
    if task_id not in TASKS:
        raise HTTPException(404, "Unknown task")
    with SessionLocal() as db:
        get_case(case_id, db)
        job = InferenceJob(id=str(uuid.uuid4()), case_id=case_id, task_id=task_id, status="queued")
        db.add(JobRecord(id=job.id, case_id=case_id, payload=job.model_dump(mode="json")))
        db.commit()
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        import redis
        try:
            redis.Redis.from_url(redis_url).lpush("oncofusion:jobs", job.id)
        except redis.RedisError:
            with SessionLocal() as db:
                db.delete(db.get(JobRecord, job.id))
                db.commit()
            raise HTTPException(503, "Job queue unavailable")
    else:
        background.add_task(run_job, job.id)
    return job


@app.get("/jobs/{job_id}", response_model=InferenceJob)
def job_status(job_id: str):
    with SessionLocal() as db:
        row = db.get(JobRecord, job_id)
        if row is None:
            raise HTTPException(404, "Job not found")
        return InferenceJob.model_validate(row.payload)


@app.get("/jobs/{job_id}/result")
def job_result(job_id: str):
    job = job_status(job_id)
    if job.status != "completed":
        raise HTTPException(409, f"Job status: {job.status}")
    return job.prediction
