from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db.session import get_session
from app.db.models import Study, Finding, Report


router = APIRouter(prefix="/api/studies")


@router.get("/{study_id}")
def get_study(study_id: int) -> dict:
    session = get_session()
    try:
        study = session.get(Study, study_id)
        if not study:
            raise HTTPException(status_code=404, detail="study not found")
        findings = (
            session.query(Finding)
            .filter(Finding.study_id == study_id)
            .order_by(Finding.id.asc())
            .all()
        )
        reports = (
            session.query(Report)
            .filter(Report.study_id == study_id)
            .order_by(Report.id.asc())
            .all()
        )
        return {
            "study": {
                "id": study.id,
                "patient_id": study.patient_id,
                "modality": study.modality,
                "image_s3_key": study.image_s3_key,
                "created_at": study.created_at.isoformat() if hasattr(study, "created_at") and study.created_at else None,
            },
            "findings": [
                {
                    "id": f.id,
                    "label": f.label,
                    "confidence": f.confidence,
                    "model_name": f.model_name,
                    "model_version": f.model_version,
                }
                for f in findings
            ],
            "reports": [
                {
                    "id": r.id,
                    "text": r.text,
                    "summary_model": r.summary_model,
                }
                for r in reports
            ],
        }
    finally:
        session.close()
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_session
from app.db.models import Study, Finding
from app.services.storage import get_s3_storage
from pydantic import BaseModel

router = APIRouter(prefix="/api/studies")

class Bbox(BaseModel):
    x: float
    y: float
    width: float
    height: float

class FindingOut(BaseModel):
    id: int
    label: str
    confidence: float
    bbox: Bbox

class StudyOut(BaseModel):
    image_url: str
    findings: list[FindingOut]

@router.get("/{study_id}", response_model=StudyOut)
def get_study(study_id: int, session=Depends(get_session), s3=Depends(get_s3_storage)):
    study = session.get(Study, study_id)
    if not study:
        raise HTTPException(404)
    findings = session.query(Finding).filter_by(study_id=study_id).all()
    out_findings = []
    for f in findings:
        # Stub bbox for demo
        bbox = Bbox(x=100, y=100, width=200, height=150)
        out_findings.append(FindingOut(id=f.id, label=f.label, confidence=f.confidence, bbox=bbox))
    image_url = s3._client.generate_presigned_url("get_object", Params={"Bucket": s3._bucket, "Key": study.image_s3_key}, ExpiresIn=3600)
    return StudyOut(image_url=image_url, findings=out_findings)
