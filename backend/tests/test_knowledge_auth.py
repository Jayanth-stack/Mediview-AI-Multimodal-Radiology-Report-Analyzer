from fastapi.testclient import TestClient

from app.main import app


def test_knowledge_documents_requires_authentication():
    response = TestClient(app).get("/api/knowledge/documents")

    assert response.status_code == 401
