from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import time
import redis.asyncio as aioredis  # type: ignore
from app.core.config import settings
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


async def _sse_generator(job_id: str):
    # Use Redis pubsub channel per job
    redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"jobs:{job_id}")
        # send an initial ping
        yield f"event: ping\ndata: {json.dumps({'ts': time.time()})}\n\n"
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            data = msg.get("data")
            yield f"data: {data}\n\n"
    finally:
        await redis.close()


@router.get("/{job_id}/events")
async def job_events(job_id: str) -> StreamingResponse:
    return StreamingResponse(_sse_generator(job_id), media_type="text/event-stream")


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

