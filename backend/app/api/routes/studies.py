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
    image_url = s3.generate_presigned_url("get_object", Params={"Bucket": s3._bucket, "Key": study.image_s3_key}, ExpiresIn=3600)
    return StudyOut(image_url=image_url, findings=out_findings)
