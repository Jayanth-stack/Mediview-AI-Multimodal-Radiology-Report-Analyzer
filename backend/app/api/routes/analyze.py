from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional

from app.schemas.entities import AnalysisResponse
from app.services.hf import get_hf_service


router = APIRouter(prefix="/api")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    image: UploadFile = File(...),
    report_text: Optional[str] = Form(None),
    patient_context: Optional[str] = Form(None),
    hf_service=Depends(get_hf_service),
) -> AnalysisResponse:
    return await hf_service.analyze(image=image, report_text=report_text, patient_context=patient_context)

