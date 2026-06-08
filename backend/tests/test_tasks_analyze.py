from __future__ import annotations

import unittest
from unittest.mock import patch

from app.db.models import Finding, Job, Study
from app.schemas.entities import AnalysisResponse, Finding as SchemaFinding
from app.tasks import analyze as analyze_module
from tests.utils import build_test_db


class _FakePublisher:
    def __init__(self):
        self.events = []

    def publish(self, channel: str, payload: str):
        self.events.append((channel, payload))


class _FakeS3:
    def get_object_bytes(self, key: str) -> bytes:
        return b"fake-image-bytes"


class _FakeGemini:
    def __init__(self):
        self.calls = []

    def analyze_bytes(self, **kwargs):
        self.calls.append(kwargs)
        return AnalysisResponse(
            findings=[
                SchemaFinding(label="left basilar opacity", confidence=0.91),
            ],
            summary="Opacity at left base.",
            notes=None,
        )


class _FailingGemini:
    def analyze_bytes(self, **kwargs):
        raise RuntimeError("Gemini unavailable")


class AnalyzeTaskTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.SessionLocal = build_test_db()

    def tearDown(self):
        self.engine.dispose()

    def _seed_job(self, job_id: str):
        session = self.SessionLocal()
        try:
            session.add(
                Job(
                    id=job_id,
                    user_id=42,
                    type="analyze",
                    status="queued",
                    progress=0,
                    s3_key="uploads/a.png",
                )
            )
            session.commit()
        finally:
            session.close()

    def test_analyze_task_success_path_persists_results(self):
        self._seed_job("job-success")
        fake_publisher = _FakePublisher()
        fake_gemini = _FakeGemini()

        with (
            patch("app.tasks.analyze.get_session", side_effect=self.SessionLocal),
            patch("app.tasks.analyze.get_s3_storage", return_value=_FakeS3()),
            patch("app.tasks.analyze.get_gemini_service", return_value=fake_gemini),
            patch("app.tasks.analyze.redis_sync.from_url", return_value=fake_publisher),
        ):
            analyze_module.analyze_task.run(
                job_id="job-success",
                s3_key="uploads/a.png",
                report_text="short history",
            )

        session = self.SessionLocal()
        try:
            job = session.get(Job, "job-success")
            self.assertIsNotNone(job)
            self.assertEqual(job.status, "completed")
            self.assertEqual(job.progress, 100)
            self.assertEqual(job.result["summary"], "Opacity at left base.")
            self.assertEqual(job.result["s3_key"], "uploads/a.png")

            studies = session.query(Study).all()
            findings = session.query(Finding).all()
            self.assertEqual(len(studies), 1)
            self.assertEqual(len(findings), 1)
            self.assertEqual(studies[0].user_id, 42)
            self.assertEqual(findings[0].label, "left basilar opacity")
        finally:
            session.close()

        self.assertEqual(
            fake_gemini.calls,
            [{"image_bytes": b"fake-image-bytes", "report_text": "short history"}],
        )
        self.assertGreater(len(fake_publisher.events), 0)

    def test_analyze_task_falls_back_to_stub_findings_when_gemini_fails(self):
        self._seed_job("job-fallback")

        with (
            patch("app.tasks.analyze.get_session", side_effect=self.SessionLocal),
            patch("app.tasks.analyze.get_s3_storage", return_value=_FakeS3()),
            patch("app.tasks.analyze.get_gemini_service", return_value=_FailingGemini()),
            patch("app.tasks.analyze.redis_sync.from_url", side_effect=RuntimeError("redis down")),
        ):
            analyze_module.analyze_task.run(
                job_id="job-fallback",
                s3_key="uploads/b.png",
                report_text=None,
            )

        session = self.SessionLocal()
        try:
            job = session.get(Job, "job-fallback")
            self.assertIsNotNone(job)
            self.assertEqual(job.status, "completed")
            self.assertEqual(job.progress, 100)
            self.assertEqual(job.result["summary"], "Automated analysis complete (stub).")
            self.assertEqual(job.result["findings"][0]["label"], "possible_abnormality")
            self.assertEqual(job.result["s3_key"], "uploads/b.png")
        finally:
            session.close()

    def test_analyze_task_returns_cleanly_when_job_is_missing(self):
        with (
            patch("app.tasks.analyze.get_session", side_effect=self.SessionLocal),
            patch("app.tasks.analyze.get_s3_storage", return_value=_FakeS3()),
            patch("app.tasks.analyze.get_gemini_service", return_value=_FakeGemini()),
        ):
            analyze_module.analyze_task.run(
                job_id="does-not-exist",
                s3_key="uploads/missing.png",
                report_text=None,
            )

        session = self.SessionLocal()
        try:
            self.assertEqual(session.query(Job).count(), 0)
            self.assertEqual(session.query(Study).count(), 0)
            self.assertEqual(session.query(Finding).count(), 0)
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()

