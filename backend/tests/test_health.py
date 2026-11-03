from unittest.mock import patch


def test_health_check_healthy(client):
    """
    Test GET /health returns 200 and 'connected' when database is accessible.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["project"] == "Aqua Rover Backend"
    assert "environment" in data
    assert "timestamp" in data


def test_health_check_database_down(client):
    """
    Test GET /health returns 503 and 'disconnected' when database is unreachable.
    """
    with patch("app.api.routes.health.check_db_health", return_value=False):
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"
        assert "timestamp" in data
