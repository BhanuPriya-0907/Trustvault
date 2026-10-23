
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_auth_health_endpoint():
    response = client.get("/auth/health")

    assert response.status_code == 200


def test_documents_health_endpoint():
    response = client.get("/documents/health")

    assert response.status_code == 200

