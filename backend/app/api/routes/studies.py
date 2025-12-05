from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.db.session import get_session
from app.db.models import Study, Finding, Report, User
from app.services.storage import get_s3_storage
from app.api import deps

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
    id: int
    image_url: str
    findings: list[FindingOut]
    patient_id: str
    modality: str
    created_at: str | None


@router.get("/{study_id}", response_model=StudyOut)
def get_study(
    study_id: int,
    session=Depends(get_session),
    s3=Depends(get_s3_storage),
    current_user: User = Depends(deps.get_current_user),
):
    study = session.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="study not found")
        
    findings = (
        session.query(Finding)
        .filter(Finding.study_id == study_id)
        .order_by(Finding.id.asc())
        .all()
    )
    
    out_findings = []
    for f in findings:
        # Stub bbox for demo - in real app this would come from DB or JSON extra field
        bbox = Bbox(x=100, y=100, width=200, height=150)
        out_findings.append(FindingOut(id=f.id, label=f.label, confidence=f.confidence, bbox=bbox))
        
    try:
        image_url = s3._client.generate_presigned_url(
            "get_object", 
            Params={"Bucket": s3._bucket, "Key": study.image_s3_key}, 
            ExpiresIn=3600
        )
    except Exception as e:
        print(f"Error generating presigned url: {e}")
        image_url = ""

    return StudyOut(
        id=study.id,
        image_url=image_url, 
        findings=out_findings,
        patient_id=study.patient_id,
        modality=study.modality,
        created_at=study.created_at.isoformat() if hasattr(study, "created_at") and study.created_at else None
    )
