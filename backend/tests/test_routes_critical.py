from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from fastapi.routing import APIRoute
from jose import jwt

from app.api import deps
from app.api.routes import analyze_job, jobs, knowledge, login, studies, uploads
from app.core import security
from app.core.config import settings
from app.db.models import Finding, Job, Study, User
from tests.utils import build_test_db


class CriticalRouteTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.SessionLocal = build_test_db()

    def tearDown(self):
        self.engine.dispose()

    def _create_user(self, email: str = "doctor@example.com", password: str = "secret") -> User:
        session = self.SessionLocal()
        try:
            user = User(
                full_name="Doctor",
                email=email,
                hashed_password=security.get_password_hash(password),
                is_active=True,
                is_superuser=False,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    def test_login_access_token_success(self):
        user = self._create_user()
        session = self.SessionLocal()
        try:
            form_data = SimpleNamespace(username=user.email, password="secret")
            out = login.login_access_token(session=session, form_data=form_data)
            payload = jwt.decode(out["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            self.assertEqual(out["token_type"], "bearer")
            self.assertEqual(payload["sub"], str(user.id))
        finally:
            session.close()

    def test_login_access_token_invalid_password(self):
        user = self._create_user()
        session = self.SessionLocal()
        try:
            with self.assertRaises(HTTPException) as ctx:
                login.login_access_token(
                    session=session,
                    form_data=SimpleNamespace(username=user.email, password="incorrect"),
                )
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertEqual(ctx.exception.detail, "Incorrect email or password")
        finally:
            session.close()

    def test_uploads_presign_put(self):
        fake_s3 = Mock()
        fake_s3.generate_presigned_put.return_value = "https://signed.example/upload-put"
        body = uploads.PresignRequest(filename="xray.png", content_type="image/png", use_post=False)

        out = uploads.presign(body=body, s3=fake_s3, current_user=object())

        self.assertEqual(out.method, "PUT")
        self.assertEqual(out.url, "https://signed.example/upload-put")
        self.assertIsNone(out.fields)
        self.assertTrue(out.key.startswith("uploads/"))
        self.assertTrue(out.key.endswith("-xray.png"))

    def test_uploads_presign_post(self):
        fake_s3 = Mock()
        fake_s3.generate_presigned_post.return_value = {
            "url": "https://signed.example/upload-post",
            "fields": {"key": "value"},
        }
        body = uploads.PresignRequest(filename="xray.png", content_type="image/png", use_post=True)

        out = uploads.presign(body=body, s3=fake_s3, current_user=object())

        self.assertEqual(out.method, "POST")
        self.assertEqual(out.url, "https://signed.example/upload-post")
        self.assertEqual(out.fields, {"key": "value"})
        self.assertTrue(out.key.startswith("uploads/"))
        self.assertTrue(out.key.endswith("-xray.png"))

    def test_knowledge_routes_require_authenticated_user(self):
        knowledge_routes = [
            route
            for route in knowledge.router.routes
            if isinstance(route, APIRoute)
        ]
        self.assertGreater(len(knowledge_routes), 0)

        for route in knowledge_routes:
            dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
            self.assertIn(deps.get_current_user, dependency_calls, route.path)

    def test_analyze_start_creates_job_and_dispatches_task(self):
        with (
            patch("app.api.routes.analyze_job.get_session", side_effect=self.SessionLocal),
            patch("app.api.routes.analyze_job.analyze_task.delay") as mock_delay,
        ):
            out = analyze_job.start_analyze(
                body=analyze_job.StartAnalyzeRequest(
                    s3_key="uploads/study-1.png",
                    report_text="patient with cough",
                ),
                current_user=object(),
            )

        session = self.SessionLocal()
        try:
            job = session.get(Job, out.job_id)
            self.assertIsNotNone(job)
            self.assertEqual(job.status, "queued")
            self.assertEqual(job.progress, 0)
            self.assertEqual(job.s3_key, "uploads/study-1.png")
        finally:
            session.close()

        mock_delay.assert_called_once_with(
            job_id=out.job_id,
            s3_key="uploads/study-1.png",
            report_text="patient with cough",
        )

    def test_jobs_get_job_returns_status(self):
        session = self.SessionLocal()
        try:
            session.add(
                Job(
                    id="job-1",
                    type="analyze",
                    status="running",
                    progress=40,
                    s3_key="uploads/study-1.png",
                    result={"hello": "world"},
                )
            )
            session.commit()
        finally:
            session.close()

        with patch("app.api.routes.jobs.get_session", side_effect=self.SessionLocal):
            out = jobs.get_job(job_id="job-1", current_user=object())

        self.assertEqual(out.id, "job-1")
        self.assertEqual(out.status, "running")
        self.assertEqual(out.progress, 40)
        self.assertEqual(out.result, {"hello": "world"})

    def test_jobs_get_job_not_found(self):
        with patch("app.api.routes.jobs.get_session", side_effect=self.SessionLocal):
            with self.assertRaises(HTTPException) as ctx:
                jobs.get_job(job_id="missing-job", current_user=object())
        self.assertEqual(ctx.exception.status_code, 404)

    def test_studies_get_study_maps_findings_and_signed_url(self):
        session = self.SessionLocal()
        try:
            study = Study(patient_id="P-001", modality="XR", image_s3_key="uploads/xray.png")
            session.add(study)
            session.commit()
            session.refresh(study)
            session.add(
                Finding(
                    study_id=study.id,
                    label="right lower lobe opacity",
                    confidence=0.88,
                    model_name="gemini",
                    model_version="1.5",
                )
            )
            session.commit()

            fake_s3 = Mock()
            fake_s3.generate_presigned_get.return_value = "https://signed.example/study-view"

            out = studies.get_study(study_id=study.id, session=session, s3=fake_s3, current_user=object())
        finally:
            session.close()

        self.assertEqual(out.id, study.id)
        self.assertEqual(out.patient_id, "P-001")
        self.assertEqual(out.modality, "XR")
        self.assertEqual(out.image_url, "https://signed.example/study-view")
        self.assertEqual(len(out.findings), 1)
        self.assertEqual(out.findings[0].label, "right lower lobe opacity")
        self.assertEqual(out.findings[0].bbox.x, 100)
        fake_s3.generate_presigned_get.assert_called_once_with("uploads/xray.png")

    def test_studies_get_study_not_found(self):
        session = self.SessionLocal()
        try:
            fake_s3 = SimpleNamespace(_client=Mock(), _bucket="mediview")
            with self.assertRaises(HTTPException) as ctx:
                studies.get_study(study_id=9999, session=session, s3=fake_s3, current_user=object())
        finally:
            session.close()

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail, "study not found")


if __name__ == "__main__":
    unittest.main()

