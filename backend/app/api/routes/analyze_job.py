from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4

from app.db.session import get_session
from app.db.models import Job, User
from app.tasks.analyze import analyze_task
from app.api import deps


router = APIRouter(prefix="/api/analyze")


from typing import Optional

class StartAnalyzeRequest(BaseModel):
    s3_key: str
    report_text: Optional[str] = None


class StartAnalyzeResponse(BaseModel):
    job_id: str


@router.post("/start", response_model=StartAnalyzeResponse)
def start_analyze(
    body: StartAnalyzeRequest,
    current_user: User = Depends(deps.get_current_user),
) -> StartAnalyzeResponse:
    if not body.s3_key.startswith(f"users/{current_user.id}/uploads/"):
        raise HTTPException(status_code=403, detail="upload key is not owned by current user")

    job_id = uuid4().hex
    session = get_session()
    try:
        job = Job(
            id=job_id,
            user_id=current_user.id,
            type="analyze",
            status="queued",
            progress=0,
            s3_key=body.s3_key,
        )
        session.add(job)
        session.commit()
    finally:
        session.close()

    analyze_task.delay(job_id=job_id, s3_key=body.s3_key, report_text=body.report_text)
    return StartAnalyzeResponse(job_id=job_id)

