from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4

from app.db.session import get_session
from app.db.models import Job
from app.tasks.analyze import analyze_task


router = APIRouter(prefix="/api/analyze")


class StartAnalyzeRequest(BaseModel):
    s3_key: str
    report_text: str | None = None


class StartAnalyzeResponse(BaseModel):
    job_id: str


@router.post("/start", response_model=StartAnalyzeResponse)
def start_analyze(body: StartAnalyzeRequest) -> StartAnalyzeResponse:
    job_id = uuid4().hex
    session = get_session()
    try:
        job = Job(id=job_id, type="analyze", status="queued", progress=0, s3_key=body.s3_key)
        session.add(job)
        session.commit()
    finally:
        session.close()

    analyze_task.delay(job_id=job_id, s3_key=body.s3_key, report_text=body.report_text)
    return StartAnalyzeResponse(job_id=job_id)

