from unittest.mock import patch
from scripts.seed_rover import seed_rover


def test_status_code_200_ok(client, db_session):
    """Verify 200 OK on GET endpoints."""
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)
    # /health
    r_health = client.get("/health")
    assert r_health.status_code == 200

    # /rovers
    r_rovers = client.get("/rovers")
    assert r_rovers.status_code == 200

    # /rovers/{id}
    r_rover = client.get("/rovers/AR-001")
    assert r_rover.status_code == 200

    # Ingest telemetry for status and location
    client.post(
        "/rover/telemetry",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T12:00:00Z",
            "battery": 80.0,
            "speed": 1.0,
            "latitude": 15.0,
            "longitude": 75.0,
            "status": "moving",
        },
    )

    # /rover/status
    r_status = client.get("/rover/status?rover_id=AR-001")
    assert r_status.status_code == 200

    # /rover/location
    r_loc = client.get("/rover/location?rover_id=AR-001")
    assert r_loc.status_code == 200

    # /detections
    r_det = client.get("/detections")
    assert r_det.status_code == 200


def test_status_code_201_created(client, db_session):
    """Verify 201 Created on POST ingestion and registration endpoints."""
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)

    # POST /rovers -> 201
    r_rover = client.post("/rovers", json={"rover_id": "AR-201", "name": "Rover 201"})
    assert r_rover.status_code == 201

    # POST /rover/telemetry -> 201
    r_telemetry = client.post(
        "/rover/telemetry",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T12:00:00Z",
            "battery": 88.0,
            "speed": 0.5,
            "latitude": 14.5,
            "longitude": 74.5,
            "status": "moving",
        },
    )
    assert r_telemetry.status_code == 201

    # POST /detections -> 201
    r_det = client.post(
        "/detections",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T12:00:00Z",
            "detections": [
                {
                    "class_name": "plastic",
                    "confidence": 0.92,
                    "bbox": [10.0, 10.0, 50.0, 50.0],
                }
            ],
        },
    )
    assert r_det.status_code == 201


def test_status_code_404_not_found(client):
    """Verify 404 Not Found when referencing non-existent entities."""
    # Unknown rover on GET /rovers/{id}
    assert client.get("/rovers/DOES_NOT_EXIST").status_code == 404

    # Unknown rover on GET /rover/status
    assert client.get("/rover/status?rover_id=DOES_NOT_EXIST").status_code == 404

    # Unknown rover on GET /rover/location
    assert client.get("/rover/location?rover_id=DOES_NOT_EXIST").status_code == 404

    # Unknown rover on POST /rover/telemetry
    assert (
        client.post(
            "/rover/telemetry",
            json={
                "rover_id": "DOES_NOT_EXIST",
                "timestamp": "2026-10-06T12:00:00Z",
                "battery": 50.0,
                "speed": 1.0,
                "latitude": 10.0,
                "longitude": 70.0,
                "status": "moving",
            },
        ).status_code
        == 404
    )

    # Unknown rover on POST /detections
    assert (
        client.post(
            "/detections",
            json={
                "rover_id": "DOES_NOT_EXIST",
                "timestamp": "2026-10-06T12:00:00Z",
                "detections": [
                    {
                        "class_name": "plastic",
                        "confidence": 0.9,
                        "bbox": [10.0, 10.0, 20.0, 20.0],
                    }
                ],
            },
        ).status_code
        == 404
    )


def test_status_code_409_conflict(client):
    """Verify 409 Conflict when attempting to register duplicate rover_id."""
    payload = {"rover_id": "AR-CONFLICT", "name": "Conflict Rover"}
    r1 = client.post("/rovers", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/rovers", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"].lower()


def test_status_code_422_unprocessable_entity(client, db_session):
    """Verify 422 Unprocessable Entity on schema validation failure."""
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)

    # Missing mandatory fields on rover creation
    assert client.post("/rovers", json={}).status_code == 422

    # Battery > 100 on telemetry
    assert (
        client.post(
            "/rover/telemetry",
            json={
                "rover_id": "AR-001",
                "timestamp": "2026-10-06T12:00:00Z",
                "battery": 150.0,
                "speed": 1.0,
                "latitude": 10.0,
                "longitude": 70.0,
                "status": "moving",
            },
        ).status_code
        == 422
    )

    # Empty detections array
    assert (
        client.post(
            "/detections",
            json={
                "rover_id": "AR-001",
                "timestamp": "2026-10-06T12:00:00Z",
                "detections": [],
            },
        ).status_code
        == 422
    )


def test_status_code_503_service_unavailable(client):
    """Verify 503 Service Unavailable when database health check fails."""
    with patch("app.api.routes.health.check_db_health", return_value=False):
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"
