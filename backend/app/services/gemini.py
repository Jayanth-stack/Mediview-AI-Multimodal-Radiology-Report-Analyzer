from __future__ import annotations

from typing import Optional, List
from fastapi import UploadFile
import io
from PIL import Image
import json
import re

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.core.config import settings
from app.schemas.entities import AnalysisResponse, Finding, BoundingBox


class GeminiService:
    def __init__(self) -> None:
        self._enabled = False
        if settings.GEMINI_API_KEY and genai:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self._vision_model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)
                self._enabled = True
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")

    async def analyze(
        self,
        image: UploadFile,
        report_text: Optional[str],
        patient_context: Optional[str],
    ) -> AnalysisResponse:
        image_bytes = await image.read()
        
        if not self._enabled:
            # Deterministic stubbed response while models are not configured
            return AnalysisResponse(
                summary="No Gemini API key configured; returning stubbed summary.",
                findings=[
                    Finding(label="possible_abnormality", confidence=0.42),
                ],
                notes="Configure GEMINI_API_KEY env to enable real inference.",
            )

        findings = self.classify_bytes(image_bytes)
        
        # Summarize report text if provided
        summary_text = ""
        if report_text:
            summary_text = self.summarize_text(report_text)
        
        # If no summary from report, generate one from findings
        if not summary_text and findings:
            summary_text = self._generate_findings_summary(findings)
        
        final_summary = summary_text or "Automated analysis complete. Review findings and images."
        return AnalysisResponse(summary=final_summary, findings=findings, notes=None)

    def classify_bytes(self, image_bytes: bytes) -> list[Finding]:
        if not self._enabled:
            return [Finding(label="possible_abnormality", confidence=0.42)]
        
        try:
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            return []
        
        try:
            prompt = """Analyze this medical image and identify any findings. 
            Return a JSON array where each finding has:
            - "label": description of the finding
            - "confidence": confidence score between 0 and 1
            - "bbox": optional bounding box with x, y, width, height (in pixels)
            
            Focus on: abnormalities, pathologies, anatomical landmarks, or notable features.
            Be specific and use medical terminology where appropriate.
            
            Example format:
            [
                {
                    "label": "opacity in right upper lobe",
                    "confidence": 0.85,
                    "bbox": {"x": 120, "y": 80, "width": 100, "height": 100}
                }
            ]
            
            Return ONLY the JSON array, no other text."""
            
            response = self._vision_model.generate_content([prompt, pil_image])
            findings = self._parse_findings(response.text)
            return findings
        except Exception as e:
            print(f"Gemini vision error: {e}")
            return []

    def summarize_text(self, text: str) -> str:
        if not self._enabled or not text:
            return ""
        
        try:
            prompt = f"""Summarize this medical report concisely, focusing on key findings and recommendations.
            Keep it under 3 sentences. Use clear medical terminology.
            
            Report:
            {text[:2000]}"""
            
            response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini summarization error: {e}")
            return ""

    def _parse_findings(self, response_text: str) -> list[Finding]:
        """Parse JSON findings from Gemini response"""
        try:
            # Try to extract JSON array from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                findings = []
                for item in data:
                    bbox = None
                    if "bbox" in item and isinstance(item["bbox"], dict):
                        try:
                            bbox = BoundingBox(
                                x=float(item["bbox"].get("x", 0)),
                                y=float(item["bbox"].get("y", 0)),
                                width=float(item["bbox"].get("width", 100)),
                                height=float(item["bbox"].get("height", 100))
                            )
                        except:
                            pass
                    
                    findings.append(Finding(
                        label=item.get("label", "unknown finding"),
                        confidence=float(item.get("confidence", 0.5)),
                        bbox=bbox
                    ))
                return findings[:5]  # Limit to top 5 findings
        except Exception as e:
            print(f"Failed to parse findings: {e}")
        
        # Fallback: return a generic finding if parsing fails
        return [Finding(label="analysis completed - manual review recommended", confidence=0.5)]

    def _generate_findings_summary(self, findings: list[Finding]) -> str:
        """Generate a summary from the list of findings"""
        if not findings:
            return "No significant findings detected."
        
        high_conf = [f for f in findings if f.confidence > 0.7]
        if high_conf:
            labels = [f.label for f in high_conf[:3]]
            return f"Key findings: {', '.join(labels)}. Further clinical correlation recommended."
        else:
            return "Low confidence findings detected. Manual review strongly recommended."


_gemini_singleton: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    global _gemini_singleton
    if _gemini_singleton is None:
        _gemini_singleton = GeminiService()
    return _gemini_singleton
