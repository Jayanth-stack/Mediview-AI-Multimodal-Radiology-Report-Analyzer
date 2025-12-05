from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional

from app.schemas.entities import AnalysisResponse
from app.services.gemini import get_gemini_service
from app.api import deps


router = APIRouter(prefix="/api")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    image: UploadFile = File(...),
    report_text: Optional[str] = Form(None),
    patient_context: Optional[str] = Form(None),
    gemini_service=Depends(get_gemini_service),
    current_user=Depends(deps.get_current_user),
) -> AnalysisResponse:
    return await gemini_service.analyze(image=image, report_text=report_text, patient_context=patient_context)



