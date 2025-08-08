from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.session import get_session
from app.db.models import Job


router = APIRouter(prefix="/api/jobs")


class JobStatus(BaseModel):
    id: str
    status: str
    progress: int
    error: str | None = None
    result: dict | None = None


@router.get("/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    session = get_session()
    try:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        return JobStatus(
            id=job.id,
            status=job.status,
            progress=job.progress,
            error=job.error,
            result=job.result,
        )
    finally:
        session.close()

