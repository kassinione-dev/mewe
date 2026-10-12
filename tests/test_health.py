from sqlalchemy.exc import OperationalError

from src.app.services import health_service


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_health_without_database(client, monkeypatch):
    def broken_ping():
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(health_service, "ping_database", broken_ping)

    response = client.get("/api/health")

    assert response.status_code == 503
    assert response.json == {"error": "database unavailable"}
