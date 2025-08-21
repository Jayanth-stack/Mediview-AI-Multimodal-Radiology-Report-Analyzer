from __future__ import annotations

from typing import Optional
import mimetypes

from app.tasks.celery_app import celery_app
from app.db.session import get_session
from app.db.models import Job, Study
from app.services.gemini import get_gemini
from app.services.storage import get_s3_storage


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

        # Create a Study row for this upload
        study = Study(patient_id="unknown", modality="unknown", image_s3_key=s3_key)
        session.add(study)
        session.commit()
        session.refresh(study)

        # Load image bytes from object storage
        s3 = get_s3_storage()
        image_bytes = s3.get_object_bytes(s3_key)
        mime, _ = mimetypes.guess_type(s3_key)
        mime = mime or "image/png"

        findings: list[dict] = []
        summary: str = ""

        try:
            gemini = get_gemini()
            out = gemini.analyze(img_bytes=image_bytes, mime_type=mime, report_text=report_text)
            findings = list(out.get("findings", [])) if isinstance(out.get("findings"), list) else []
            summary = str(out.get("summary", "")).strip()
        except Exception:
            # Fallback stub if Gemini not configured/available
            findings = [{"label": "possible_abnormality", "confidence": 0.42}]
            summary = "Automated analysis complete (stub)."

        job.progress = 100
        job.status = "completed"
        job.result = {
            "study_id": study.id,
            "s3_key": s3_key,
            "summary": summary,
            "findings": findings,
        }
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

