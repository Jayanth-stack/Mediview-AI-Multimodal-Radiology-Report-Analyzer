from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import uuid4

from app.db.session import get_session
from app.db.models import Job, User
from app.tasks.analyze import analyze_task
from app.api import deps


router = APIRouter(prefix="/api/analyze")


from typing import Optional


def _user_upload_prefix(user_id: int) -> str:
    return f"users/{user_id}/uploads/"

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
    if not current_user.is_superuser and not body.s3_key.startswith(_user_upload_prefix(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="upload key does not belong to current user",
        )

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

