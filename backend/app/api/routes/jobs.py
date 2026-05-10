from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from pydantic import BaseModel
from typing import Annotated, Optional

from app.db.session import get_session
from app.db.models import Job, User
from app.api import deps
from app.core.config import settings
from jose import jwt, JWTError

router = APIRouter(prefix="/api/jobs")


class JobStatus(BaseModel):
    id: str
    status: str
    progress: int
    error: Optional[str] = None
    result: Optional[dict] = None


@router.get("/{job_id}", response_model=JobStatus)
def get_job(
    job_id: str,
    current_user: User = Depends(deps.get_current_user)
) -> JobStatus:
    session = get_session()
    try:
        job = (
            session.query(Job)
            .filter(Job.id == job_id, Job.user_id == current_user.id)
            .first()
        )
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
async def job_events(
    job_id: str, 
    request: Request,
    token: Annotated[Optional[str], Query()] = None
):
    # Manually validate token for SSE since EventSource doesn't support custom headers
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    session = get_session()
    try:
        user = session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid token")
    finally:
        session.close()

    async def event_gen():
        last_progress = -1
        last_status = None
        while True:
            if await request.is_disconnected():
                break
            session = get_session()
            try:
                job = (
                    session.query(Job)
                    .filter(Job.id == job_id, Job.user_id == user_id)
                    .first()
                )
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
