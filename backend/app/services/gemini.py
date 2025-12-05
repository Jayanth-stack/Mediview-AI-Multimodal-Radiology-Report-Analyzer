from __future__ import annotations

import io
import json
import re
from typing import Optional, Any, List
import google.generativeai as genai
from fastapi import UploadFile
from PIL import Image

from app.core.config import settings
from app.schemas.entities import AnalysisResponse, Finding, BoundingBox


class GeminiService:
    """Gemini AI service with RAG support for enhanced medical image analysis."""
    
    def __init__(self, vector_store: Optional[Any] = None) -> None:
        self._enabled = False
        self._vector_store = vector_store
        self._rag_enabled = settings.RAG_ENABLED
        
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self._vision_model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)
                self._enabled = True
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
    
    def set_vector_store(self, vector_store: Any) -> None:
        """Set the vector store for RAG functionality."""
        self._vector_store = vector_store

    async def analyze(
        self,
        image: UploadFile,
        report_text: Optional[str],
        patient_context: Optional[str],
    ) -> AnalysisResponse:
        image_bytes = await image.read()
        
        if not self._enabled:
            return AnalysisResponse(
                summary="No Gemini API key configured; returning stubbed summary.",
                findings=[
                    Finding(label="possible_abnormality", confidence=0.42),
                ],
                notes="Configure GEMINI_API_KEY env to enable real inference.",
            )

        # Run analysis with optional RAG context
        findings = self.classify_bytes_with_rag(image_bytes)
        
        # Summarize report text if provided
        summary_text = ""
        if report_text:
            summary_text = self.summarize_text(report_text)
        
        # If no summary from report, generate one from findings
        if not summary_text and findings:
            summary_text = self._generate_findings_summary(findings)
        
        final_summary = summary_text or "Automated analysis complete. Review findings and images."
        return AnalysisResponse(summary=final_summary, findings=findings, notes=None)
    
    def _retrieve_context(self, query: str) -> str:
        """Retrieve relevant medical knowledge based on query.
        
        Args:
            query: Search query (typically finding labels or medical terms)
            
        Returns:
            Formatted context string from relevant documents
        """
        if not self._vector_store or not self._rag_enabled:
            return ""
        
        try:
            docs = self._vector_store.search(query, limit=settings.RAG_TOP_K)
            
            if not docs:
                return ""
            
            # Format retrieved documents as context
            context_parts = []
            for doc in docs:
                # Limit content to avoid token overflow
                content_preview = doc.content[:1500] if len(doc.content) > 1500 else doc.content
                context_parts.append(
                    f"[Source: {doc.source}] {doc.title}:\n{content_preview}"
                )
            
            return "\n\n---\n\n".join(context_parts)
        except Exception as e:
            print(f"RAG retrieval error: {e}")
            return ""

    def classify_bytes(self, image_bytes: bytes) -> list[Finding]:
        """Basic image classification without RAG."""
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
    
    def classify_bytes_with_rag(self, image_bytes: bytes) -> list[Finding]:
        """Enhanced image classification with RAG context retrieval.
        
        This method:
        1. Performs initial image analysis
        2. Retrieves relevant medical knowledge based on findings
        3. Re-analyzes with the retrieved context for better accuracy
        """
        # Step 1: Initial classification
        initial_findings = self.classify_bytes(image_bytes)
        
        if not initial_findings or not self._vector_store or not self._rag_enabled:
            return initial_findings
        
        # Step 2: Build query from findings
        query = " ".join([f.label for f in initial_findings[:3]])  # Top 3 findings
        
        # Step 3: Retrieve context
        context = self._retrieve_context(query)
        
        if not context:
            return initial_findings
        
        # Step 4: Re-analyze with context
        try:
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            enhanced_prompt = f"""You are a radiologist assistant analyzing a medical image.
            
Based on relevant medical literature and guidelines:

{context}

---

Now analyze this medical image. Consider the reference information above to provide more accurate and detailed findings.

Return a JSON array where each finding has:
- "label": detailed description of the finding
- "confidence": confidence score between 0 and 1  
- "bbox": optional bounding box with x, y, width, height

Be specific, use proper medical terminology, and reference relevant guidelines where applicable.
Return ONLY the JSON array, no other text."""
            
            response = self._vision_model.generate_content([enhanced_prompt, pil_image])
            enhanced_findings = self._parse_findings(response.text)
            
            if enhanced_findings:
                return enhanced_findings
        except Exception as e:
            print(f"RAG-enhanced analysis error: {e}")
        
        return initial_findings

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
