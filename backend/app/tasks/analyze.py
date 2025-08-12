from __future__ import annotations

from typing import Optional

from app.tasks.celery_app import celery_app
from app.db.session import get_session
from app.db.models import Job, Study
from app.pipeline.base import Pipeline
from app.pipeline.stages import ClassifyStage, SummarizeStage, PersistStage
from app.services.hf import get_hf_service
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

        # Build pipeline context
        ctx: dict[str, object] = {
            "study": study,
            "image_bytes": image_bytes,
            "report_text": report_text or "",
        }

        hf = get_hf_service()
        pipeline = Pipeline([ClassifyStage(hf), SummarizeStage(hf), PersistStage(get_session)])

        def progress(p: int, _msg: str) -> None:
            job.status = "running"
            job.progress = max(job.progress, min(99, int(p)))
            session.commit()

        progress(10, "loaded")
        result_ctx = pipeline.run(ctx, progress)

        job.progress = 100
        job.status = "completed"
        job.result = {
            "study_id": study.id,
            "num_findings": len(result_ctx.get("findings", [])) if isinstance(result_ctx.get("findings"), list) else 0,
            "s3_key": s3_key,
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

