from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi import Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
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


@router.get("/{job_id}/events")
async def job_events(job_id: str, request: Request):
    async def event_gen():
        last_progress = -1
        last_status = None
        while True:
            if await request.is_disconnected():
                break
            session = get_session()
            try:
                job = session.get(Job, job_id)
                if not job:
                    yield {"event": "error", "data": json.dumps({"error": "not_found"})}
                    break
                if job.progress != last_progress or job.status != last_status:
                    payload = {
                        "id": job.id,
                        "status": job.status,
                        "progress": job.progress,
                        "error": job.error,
                        "result": job.result,
                    }
                    yield {"event": "progress", "data": json.dumps(payload)}
                    last_progress = job.progress
                    last_status = job.status
                if job.status in ("completed", "failed"):
                    break
            finally:
                session.close()
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_gen())

