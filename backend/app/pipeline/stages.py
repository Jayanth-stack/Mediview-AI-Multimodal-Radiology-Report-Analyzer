from __future__ import annotations

from typing import Any, Callable

from app.services.hf import HFService
from app.db.models import Study, Report, Finding


class ClassifyStage:
    def __init__(self, hf_service: HFService) -> None:
        self._hf = hf_service

    def run(self, ctx: dict[str, Any], progress: Callable[[int, str], None]) -> None:
        image_bytes: bytes = ctx["image_bytes"]
        findings = self._hf.classify_bytes(image_bytes)
        ctx["findings"] = findings
        progress(30, "classified")


class SummarizeStage:
    def __init__(self, hf_service: HFService) -> None:
        self._hf = hf_service

    def run(self, ctx: dict[str, Any], progress: Callable[[int, str], None]) -> None:
        report_text: str = ctx.get("report_text") or ""
        if not report_text:
            ctx["summary"] = ""
            return
        ctx["summary"] = self._hf.summarize_text(report_text) or ""
        progress(60, "summarized")


class PersistStage:
    def __init__(self, session_factory: Callable[[], Any]) -> None:
        self._session_factory = session_factory

    def run(self, ctx: dict[str, Any], progress: Callable[[int, str], None]) -> None:
        session = self._session_factory()
        try:
            study: Study = ctx["study"]

            # Persist findings if any
            for f in ctx.get("findings", []) or []:
                session.add(
                    Finding(
                        study_id=study.id,
                        label=getattr(f, "label", None) or (f["label"] if isinstance(f, dict) else "unknown"),
                        confidence=float(getattr(f, "confidence", 0.0) or (f.get("confidence", 0.0) if isinstance(f, dict) else 0.0)),
                        model_name=getattr(f, "model_name", None) if not isinstance(f, dict) else f.get("model_name"),
                        model_version=getattr(f, "model_version", None) if not isinstance(f, dict) else f.get("model_version"),
                        extra=getattr(f, "extra", None) if not isinstance(f, dict) else f.get("extra"),
                    )
                )

            # Persist a report row if either original text or a summary exists
            summary: str = ctx.get("summary") or ""
            report_text: str = ctx.get("report_text") or ""
            if summary or report_text:
                session.add(
                    Report(
                        study_id=study.id,
                        text=report_text or summary,
                        summary_model=None,
                    )
                )

            session.commit()
            progress(95, "persisted")
        finally:
            session.close()


