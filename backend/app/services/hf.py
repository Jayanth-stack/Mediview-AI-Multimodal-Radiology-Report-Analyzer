from __future__ import annotations

from typing import Optional, Any, List
from fastapi import UploadFile
from pydantic import BaseModel
import io
from PIL import Image

from app.core.config import settings
from app.schemas.entities import AnalysisResponse, Finding


class HFService:
    def __init__(self) -> None:
        self._pipelines: dict[str, Any] = {}
        self._enabled = any([
            settings.HF_IMG_CLS_MODEL,
            settings.HF_IMG_SEG_MODEL,
            settings.HF_VQA_MODEL,
            settings.HF_DQA_MODEL,
            settings.HF_SUMM_MODEL,
        ])

    def _load_pipeline(self, task: str, model_name: Optional[str]) -> Optional[Any]:
        if not model_name:
            return None
        if task in self._pipelines:
            return self._pipelines[task]
        try:
            from transformers import pipeline

            pipe = pipeline(task=task, model=model_name, token=settings.HF_API_TOKEN)
            self._pipelines[task] = pipe
            return pipe
        except Exception:
            return None

    async def analyze(
        self,
        image: UploadFile,
        report_text: Optional[str],
        patient_context: Optional[str],
    ) -> AnalysisResponse:
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        if not self._enabled:
            # Deterministic stubbed response while models are not configured
            return AnalysisResponse(
                summary="No models configured; returning stubbed summary.",
                findings=[
                    Finding(label="possible_abnormality", confidence=0.42),
                ],
                notes="Configure HF_* envs to enable real inference.",
            )

        findings: List[Finding] = []

        # Image classification
        cls_pipe = self._load_pipeline("image-classification", settings.HF_IMG_CLS_MODEL)
        if cls_pipe is not None:
            try:
                cls_outputs = cls_pipe(pil_image)  # type: ignore[call-arg]
                if isinstance(cls_outputs, list) and cls_outputs:
                    top = cls_outputs[0]
                    findings.append(
                        Finding(label=top.get("label", "unknown"), confidence=float(top.get("score", 0.0)))
                    )
            except Exception:
                pass

        # Summarization of provided report text
        summary_text = ""
        if report_text and (summ_pipe := self._load_pipeline("summarization", settings.HF_SUMM_MODEL)) is not None:
            try:
                out = summ_pipe(report_text[:2000])
                if isinstance(out, list) and out:
                    summary_text = out[0].get("summary_text", "")
            except Exception:
                pass

        final_summary = summary_text or "Automated analysis complete. Review findings and images."
        return AnalysisResponse(summary=final_summary, findings=findings, notes=None)

    # PR-2: lightweight helpers usable from background tasks/pipelines
    def classify_bytes(self, image_bytes: bytes) -> list[Finding]:
        try:
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            return []

        if not self._enabled:
            return [Finding(label="possible_abnormality", confidence=0.42)]

        results: list[Finding] = []
        cls_pipe = self._load_pipeline("image-classification", settings.HF_IMG_CLS_MODEL)
        if cls_pipe is not None:
            try:
                outputs = cls_pipe(pil_image)  # type: ignore[call-arg]
                if isinstance(outputs, list):
                    for item in outputs[:3]:
                        label = item.get("label", "unknown")
                        score = float(item.get("score", 0.0))
                        results.append(Finding(label=label, confidence=score))
            except Exception:
                pass
        return results

    def summarize_text(self, text: str) -> str:
        if not text:
            return ""
        if not self._enabled:
            return ""
        summ_pipe = self._load_pipeline("summarization", settings.HF_SUMM_MODEL)
        if summ_pipe is None:
            return ""
        try:
            out = summ_pipe(text[:2000])
            if isinstance(out, list) and out:
                return out[0].get("summary_text", "")
        except Exception:
            return ""
        return ""


_hf_singleton: Optional[HFService] = None


def get_hf_service() -> HFService:
    global _hf_singleton
    if _hf_singleton is None:
        _hf_singleton = HFService()
    return _hf_singleton

