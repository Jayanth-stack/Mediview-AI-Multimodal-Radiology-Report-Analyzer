from __future__ import annotations

import io
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image

from app.db.models import Document
from app.schemas.entities import Finding
from app.services.embeddings import EmbeddingService
from app.services.gemini import GeminiService
from app.services.hf import HFService
from app.services.storage import S3Storage
from app.services.vector_store import VectorStore
from tests.utils import build_test_db


class _DisabledEmbeddings:
    enabled = False

    def embed_text(self, text: str):
        return []

    def embed_query(self, query: str):
        return []


class StorageServiceTests(unittest.TestCase):
    def test_generate_presigned_put_uses_public_client(self):
        internal_client = Mock()
        public_client = Mock()
        public_client.generate_presigned_url.return_value = "https://signed.example/upload"

        with patch(
            "app.services.storage.boto3.client",
            side_effect=[internal_client, public_client],
        ):
            storage = S3Storage()
            out = storage.generate_presigned_put(
                key="uploads/case-1.png",
                content_type="image/png",
                expires_seconds=600,
            )

        self.assertEqual(out, "https://signed.example/upload")
        public_client.generate_presigned_url.assert_called_once()

    def test_generate_presigned_get_uses_public_client(self):
        internal_client = Mock()
        public_client = Mock()
        public_client.generate_presigned_url.return_value = "https://signed.example/view"

        with patch(
            "app.services.storage.boto3.client",
            side_effect=[internal_client, public_client],
        ):
            storage = S3Storage()
            out = storage.generate_presigned_get(
                key="uploads/case-1.png",
                expires_seconds=600,
            )

        self.assertEqual(out, "https://signed.example/view")
        public_client.generate_presigned_url.assert_called_once_with(
            ClientMethod="get_object",
            Params={"Bucket": "mediview", "Key": "uploads/case-1.png"},
            ExpiresIn=600,
        )
        internal_client.generate_presigned_url.assert_not_called()

    def test_get_object_bytes_reads_and_closes_stream(self):
        internal_client = Mock()
        public_client = Mock()
        body = Mock()
        body.read.return_value = b"raw-image-bytes"
        internal_client.get_object.return_value = {"Body": body}

        with patch(
            "app.services.storage.boto3.client",
            side_effect=[internal_client, public_client],
        ):
            storage = S3Storage()
            out = storage.get_object_bytes("uploads/case-2.png")

        self.assertEqual(out, b"raw-image-bytes")
        body.read.assert_called_once()
        body.close.assert_called_once()


class GeminiServiceTests(unittest.TestCase):
    def test_parse_findings_parses_json_bbox(self):
        fake_settings = SimpleNamespace(
            GEMINI_API_KEY=None,
            GEMINI_MODEL="gemini-model",
            GEMINI_VISION_MODEL="gemini-vision-model",
            RAG_ENABLED=True,
            RAG_TOP_K=5,
        )
        with patch("app.services.gemini.settings", fake_settings):
            service = GeminiService()

        findings = service._parse_findings(
            '[{"label":"small pleural effusion","confidence":0.87,'
            '"bbox":{"x":11,"y":22,"width":33,"height":44}}]'
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].label, "small pleural effusion")
        self.assertAlmostEqual(findings[0].confidence, 0.87)
        self.assertIsNotNone(findings[0].bbox)
        self.assertEqual(findings[0].bbox.x, 11.0)

    def test_parse_findings_invalid_payload_returns_fallback(self):
        fake_settings = SimpleNamespace(
            GEMINI_API_KEY=None,
            GEMINI_MODEL="gemini-model",
            GEMINI_VISION_MODEL="gemini-vision-model",
            RAG_ENABLED=True,
            RAG_TOP_K=5,
        )
        with patch("app.services.gemini.settings", fake_settings):
            service = GeminiService()

        findings = service._parse_findings("not-json")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].label, "analysis completed - manual review recommended")

    def test_generate_findings_summary_prefers_high_confidence_findings(self):
        fake_settings = SimpleNamespace(
            GEMINI_API_KEY=None,
            GEMINI_MODEL="gemini-model",
            GEMINI_VISION_MODEL="gemini-vision-model",
            RAG_ENABLED=True,
            RAG_TOP_K=5,
        )
        with patch("app.services.gemini.settings", fake_settings):
            service = GeminiService()

        summary = service._generate_findings_summary(
            [
                Finding(label="left lower lobe opacity", confidence=0.93),
                Finding(label="mild cardiomegaly", confidence=0.78),
            ]
        )
        self.assertIn("left lower lobe opacity", summary)


class VectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.SessionLocal = build_test_db()

    def tearDown(self):
        self.engine.dispose()

    def test_add_and_search_with_text_fallback_when_embeddings_disabled(self):
        session = self.SessionLocal()
        try:
            store = VectorStore(session=session, embedding_service=_DisabledEmbeddings())
            doc_id = store.add_document(
                title="Chest X-Ray Guideline",
                content="Pleural effusion can appear as blunting of the costophrenic angle.",
                source="acr",
                doc_type="guideline",
            )
            self.assertIsNotNone(doc_id)

            results = store.search("effusion", limit=5)
            self.assertGreaterEqual(len(results), 1)
            self.assertEqual(results[0].title, "Chest X-Ray Guideline")
        finally:
            session.close()

    def test_delete_returns_false_for_missing_document(self):
        session = self.SessionLocal()
        try:
            store = VectorStore(session=session, embedding_service=_DisabledEmbeddings())
            self.assertFalse(store.delete(9999))
        finally:
            session.close()

    def test_count_returns_number_of_documents(self):
        session = self.SessionLocal()
        try:
            session.add(
                Document(
                    title="Doc 1",
                    content="content",
                    source="src",
                    doc_type="guideline",
                )
            )
            session.add(
                Document(
                    title="Doc 2",
                    content="more content",
                    source="src",
                    doc_type="case",
                )
            )
            session.commit()
            store = VectorStore(session=session, embedding_service=_DisabledEmbeddings())
            self.assertEqual(store.count(), 2)
        finally:
            session.close()


class EmbeddingsServiceTests(unittest.TestCase):
    def test_embeddings_service_disabled_without_api_key(self):
        fake_settings = SimpleNamespace(
            GEMINI_API_KEY=None,
            EMBEDDING_MODEL="models/embedding-001",
        )
        with patch("app.services.embeddings.settings", fake_settings):
            service = EmbeddingService()

        self.assertFalse(service.enabled)
        self.assertEqual(service.embed_text("hello world"), [])
        self.assertEqual(service.embed_query("hello"), [])
        self.assertEqual(service.embed_batch(["a", "b"]), [])


class HFServiceTests(unittest.TestCase):
    def _png_bytes(self) -> bytes:
        image = Image.new("RGB", (4, 4), color="white")
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    def test_hf_service_returns_stub_classification_when_models_disabled(self):
        fake_settings = SimpleNamespace(
            HF_IMG_CLS_MODEL=None,
            HF_IMG_SEG_MODEL=None,
            HF_VQA_MODEL=None,
            HF_DQA_MODEL=None,
            HF_SUMM_MODEL=None,
            HF_API_TOKEN=None,
        )
        with patch("app.services.hf.settings", fake_settings):
            service = HFService()
            findings = service.classify_bytes(self._png_bytes())
            summary = service.summarize_text("some report text")

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].label, "possible_abnormality")
        self.assertEqual(summary, "")


if __name__ == "__main__":
    unittest.main()

