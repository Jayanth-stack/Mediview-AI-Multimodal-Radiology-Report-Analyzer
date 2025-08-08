from __future__ import annotations

import time
from typing import Optional

from app.tasks.celery_app import celery_app
from app.db.session import get_session
from app.db.models import Job


@celery_app.task(name="analyze_task")
def analyze_task(job_id: str, s3_key: str, report_text: Optional[str] = None) -> None:
    session = get_session()
    try:
        job = session.get(Job, job_id)
        if not job:
            return
        job.status = "running"
        job.progress = 5
        session.commit()

        # Simulate steps
        for p in (20, 40, 60, 80):
            time.sleep(0.5)
            job.progress = p
            session.commit()

        # Complete
        job.progress = 100
        job.status = "completed"
        job.result = {"message": "analysis stub complete", "s3_key": s3_key}
        session.commit()
    except Exception as e:  # pragma: no cover
        try:
            job = session.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error = str(e)
                session.commit()
        finally:
            pass
    finally:
        session.close()

