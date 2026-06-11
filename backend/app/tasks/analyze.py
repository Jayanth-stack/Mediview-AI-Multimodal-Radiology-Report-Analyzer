from __future__ import annotations

from typing import Optional

from app.tasks.celery_app import celery_app
from app.db.session import get_session
from app.db.models import Job, Study, Finding
from app.schemas.entities import AnalysisResponse
from app.services.gemini import get_gemini_service
from app.services.storage import get_s3_storage
from app.core.config import settings
import redis as redis_sync  # type: ignore
import json


@celery_app.task(name="analyze_task")
def analyze_task(job_id: str, s3_key: str, report_text: Optional[str] = None) -> None:
    session = get_session()
    publisher = None
    try:
        publisher = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        publisher = None

    def publish(event: dict) -> None:
        try:
            if publisher is not None:
                publisher.publish(f"jobs:{job_id}", json.dumps(event))
        except Exception:
            pass
    try:
        job = session.get(Job, job_id)
        if not job:
            return
        job.status = "running"
        job.progress = 5
        session.commit()
        publish({"status": job.status, "progress": job.progress, "step": "started"})

        # Create a Study row for this upload
        study = Study(patient_id="unknown", modality="unknown", image_s3_key=s3_key)
        session.add(study)
        session.commit()
        session.refresh(study)
        publish({"status": job.status, "progress": 10, "step": "study_created", "study_id": study.id})

        # Load image bytes from object storage
        s3 = get_s3_storage()
        image_bytes = s3.get_object_bytes(s3_key)
        publish({"status": job.status, "progress": 20, "step": "image_loaded"})

        gemini = get_gemini_service()
        publish({"status": job.status, "progress": 30, "step": "gemini_call"})
        analysis: AnalysisResponse = gemini.analyze_bytes(
            image_bytes=image_bytes,
            report_text=report_text,
        )
        findings = [finding.model_dump(exclude_none=True) for finding in analysis.findings]
        summary = analysis.summary.strip()
        publish({"status": job.status, "progress": 80, "step": "gemini_done"})

        # Persist findings rows
        for f in findings:
            try:
                lbl = str(f.get("label", "")).strip()
                conf = float(f.get("confidence", 0.0))
                extra = {"bbox": f["bbox"]} if isinstance(f.get("bbox"), dict) else None
                row = Finding(
                    study_id=study.id,
                    label=lbl,
                    confidence=conf,
                    model_name="gemini",
                    model_version="1.5",
                    extra=extra,
                )
                session.add(row)
            except Exception:
                continue
        session.commit()
        publish({"status": job.status, "progress": 90, "step": "findings_persisted", "num_findings": len(findings)})

        job.progress = 100
        job.status = "completed"
        job.result = {
            "study_id": study.id,
            "s3_key": s3_key,
            "summary": summary,
            "findings": findings,
        }
        session.commit()
        publish({"status": job.status, "progress": job.progress, "step": "completed"})
    except Exception as e:  # pragma: no cover
        try:
            job = session.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error = str(e)
                session.commit()
                publish({"status": job.status, "progress": job.progress, "step": "failed", "error": job.error})
        finally:
            pass
    finally:
        session.close()

