import logging
from pathlib import Path
from uuid import UUID, uuid4
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import Job, get_db, init_db
from app.schemas import BatchRequest, FetchRequest, FileResponse as FetchFiles, JobResponse, JobStatus
from app.services.document_generator import generate_docx
from app.services.fetcher import FetchError, fetch_source
from app.services.parser import parse_source
from app.services.pdf_generator import generate_pdf
from app.services.storage import LocalStorage

logging.basicConfig(level=get_settings().log_level)
settings = get_settings(); app = FastAPI(title="Fetcher API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[item.strip() for item in settings.cors_origins.split(",")], allow_methods=["*"], allow_headers=["*"])
@app.on_event("startup")
def startup(): init_db()

def public_job(job: Job) -> JobResponse: return JobResponse(job_id=UUID(str(job.id)), status=JobStatus(job.status), progress=job.progress, source_url=job.source_url)
async def process_job(job_id: str) -> None:
    db = next(get_db()); job = db.get(Job, job_id)
    try:
        job.status, job.progress = "fetching", 10; db.commit()
        source = await fetch_source(job.source_url, settings)
        job.status, job.progress = "parsing", 35; db.commit()
        document = parse_source(source.url, source.final_url, source.content)
        if document.statistics.word_count < 5: raise FetchError("EXTRACTION_FAILED", "The page did not contain enough readable content.")
        job.status, job.progress = "cleaning", 55; db.commit()
        job.status, job.progress = "generating", 70; db.commit()
        files = LocalStorage(settings).save(document, generate_docx(document), generate_pdf(document))
        job.document_json = document.model_dump(mode="json"); job.files = files; job.status, job.progress = "completed", 100; db.commit()
    except FetchError as exc:
        job.status, job.progress, job.error = "failed", 100, {"code": exc.code, "message": str(exc), "retryable": exc.retryable}; db.commit()
    except Exception:
        logging.exception("job=%s failed", job_id); job.status, job.progress, job.error = "failed", 100, {"code": "PROCESSING_ERROR", "message": "The fetch could not be completed.", "retryable": False}; db.commit()
    finally: db.close()

@app.get("/api/v1/health")
def health(): return {"status": "ok", "service": "fetcher"}
@app.post("/api/v1/fetch", response_model=JobResponse, status_code=202)
async def create_fetch(request: FetchRequest, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = Job(id=str(uuid4()), source_url=str(request.url), status="queued", progress=0); db.add(job); db.commit(); tasks.add_task(process_job, job.id); return public_job(job)
@app.post("/api/v1/fetch/batch", status_code=202)
async def create_batch(request: BatchRequest, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    jobs = []
    for url in request.urls:
        job = Job(id=str(uuid4()), source_url=str(url), status="queued", progress=0); db.add(job); jobs.append(job)
    db.commit()
    for job in jobs: tasks.add_task(process_job, job.id)
    return {"batch_id": str(uuid4()), "jobs": [public_job(job).model_dump(mode="json") for job in jobs]}
@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(Job, str(job_id))
    if not job: raise HTTPException(404, detail={"code": "JOB_NOT_FOUND", "message": "Job not found."})
    return public_job(job)
@app.get("/api/v1/jobs/{job_id}/result")
def get_result(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(Job, str(job_id))
    if not job: raise HTTPException(404, detail={"code": "JOB_NOT_FOUND", "message": "Job not found."})
    if job.status != "completed": raise HTTPException(409, detail=job.error or {"code": "JOB_NOT_COMPLETE", "message": "Job is not complete."})
    return job.document_json
@app.get("/api/v1/jobs/{job_id}/files", response_model=FetchFiles)
def get_files(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(Job, str(job_id))
    if not job: raise HTTPException(404, detail={"code": "JOB_NOT_FOUND", "message": "Job not found."})
    return job.files or {}
@app.get("/api/v1/jobs/{job_id}/files/{kind}")
def download_file(job_id: UUID, kind: str, db: Session = Depends(get_db)):
    job = db.get(Job, str(job_id)); path = (job.files or {}).get(kind) if job else None
    if not path or kind not in {"json", "docx", "pdf"} or not Path(path).is_file(): raise HTTPException(404, detail={"code": "FILE_NOT_FOUND", "message": "File not found."})
    return FileResponse(path, filename=Path(path).name)
