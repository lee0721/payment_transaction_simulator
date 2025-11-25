"""
Basic FastAPI smoke tests so pytest has at least one assertion to run in CI.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_redirect():
    response = client.get("/")
    assert response.status_code == 200
