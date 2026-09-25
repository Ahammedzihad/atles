from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check_status_code():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_payload():
    response = client.get("/health")
    data = response.json()
    assert data == {"status": "ok", "service": "Atles backend"}
    assert data["status"] == "ok"
    assert data["service"] == "Atles backend"
