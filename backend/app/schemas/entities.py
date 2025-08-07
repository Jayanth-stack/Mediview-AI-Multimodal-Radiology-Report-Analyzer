from pydantic import BaseModel, Field
from typing import Optional, List


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Finding(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None


class AnalysisResponse(BaseModel):
    summary: str
    findings: List[Finding]
    notes: Optional[str] = None

