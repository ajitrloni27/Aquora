import pytest
from app.models.location import Location
from app.models.telemetry import Telemetry
from scripts.seed_rover import seed_rover


def test_post_telemetry_creates_telemetry_and_location(client, db_session):
    """
    Test POST /rover/telemetry validates and stores telemetry AND ALSO writes
    a Location row from its latitude/longitude in ONE transaction.
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)

    payload = {
        "rover_id": "AR-001",
        "timestamp": "2026-10-06T10:30:00Z",
        "battery": 82.5,
        "speed": 0.8,
        "latitude": 12.345678,
        "longitude": 74.123456,
        "status": "moving",
        "temperature": 28.5,
        "signal": 95.0,
    }

    response = client.post("/rover/telemetry", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["rover_id"] == "AR-001"
    assert data["battery"] == 82.5
    assert data["speed"] == 0.8
    assert data["status"] == "moving"
    assert data["temperature"] == 28.5
    assert data["signal"] == 95.0
    assert "id" in data

    # Verify both Telemetry and Location rows were created in the database
    telemetry_record = (
        db_session.query(Telemetry)
        .filter(Telemetry.rover_id == "AR-001")
        .order_by(Telemetry.id.desc())
        .first()
    )
    assert telemetry_record is not None
    assert telemetry_record.battery == 82.5

    location_record = (
        db_session.query(Location)
        .filter(Location.rover_id == "AR-001")
        .order_by(Location.id.desc())
        .first()
    )
    assert location_record is not None
    assert location_record.latitude == 12.345678
    assert location_record.longitude == 74.123456


def test_post_telemetry_unknown_rover(client):
    """
    Test POST /rover/telemetry returns 404 when rover_id does not exist.
    """
    payload = {
        "rover_id": "NONEXISTENT-999",
        "timestamp": "2026-10-06T10:30:00Z",
        "battery": 80.0,
        "speed": 1.0,
        "latitude": 15.0,
        "longitude": 75.0,
        "status": "moving",
    }
    response = client.post("/rover/telemetry", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.parametrize(
    "bad_payload",
    [
        # Battery > 100
        {
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:30:00Z",
            "battery": 105.0,
            "speed": 1.0,
            "latitude": 15.0,
            "longitude": 75.0,
            "status": "moving",
        },
        # Battery < 0
        {
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:30:00Z",
            "battery": -5.0,
            "speed": 1.0,
            "latitude": 15.0,
            "longitude": 75.0,
            "status": "moving",
        },
        # Speed < 0
        {
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:30:00Z",
            "battery": 50.0,
            "speed": -1.0,
            "latitude": 15.0,
            "longitude": 75.0,
            "status": "moving",
        },
        # Latitude out of bounds (> 90)
        {
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:30:00Z",
            "battery": 50.0,
            "speed": 1.0,
            "latitude": 95.0,
            "longitude": 75.0,
            "status": "moving",
        },
        # Longitude out of bounds (< -180)
        {
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:30:00Z",
            "battery": 50.0,
            "speed": 1.0,
            "latitude": 15.0,
            "longitude": -185.0,
            "status": "moving",
        },
        # Missing required latitude/longitude
        {
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:30:00Z",
            "battery": 50.0,
            "speed": 1.0,
            "status": "moving",
        },
    ],
)
def test_post_telemetry_validation_errors(client, db_session, bad_payload):
    """
    Test POST /rover/telemetry returns 422 for invalid payloads.
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)
    response = client.post("/rover/telemetry", json=bad_payload)
    assert response.status_code == 422


def test_get_rover_status_and_location_success(client, db_session):
    """
    Test GET /rover/status and GET /rover/location return latest records.
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)

    # Ingest first reading
    client.post(
        "/rover/telemetry",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:00:00Z",
            "battery": 90.0,
            "speed": 0.5,
            "latitude": 10.0,
            "longitude": 70.0,
            "status": "idle",
        },
    )

    # Ingest second reading (latest)
    client.post(
        "/rover/telemetry",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:15:00Z",
            "battery": 85.0,
            "speed": 1.2,
            "latitude": 10.5,
            "longitude": 70.5,
            "status": "moving",
        },
    )

    # GET /rover/status default (AR-001)
    status_resp = client.get("/rover/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["battery"] == 85.0
    assert status_data["speed"] == 1.2
    assert status_data["status"] == "moving"

    # GET /rover/location default (AR-001)
    loc_resp = client.get("/rover/location")
    assert loc_resp.status_code == 200
    loc_data = loc_resp.json()
    assert loc_data["latitude"] == 10.5
    assert loc_data["longitude"] == 70.5


def test_get_status_and_location_unknown_rover(client):
    """
    Test GET /rover/status and GET /rover/location return 404 for unknown rover.
    """
    resp_status = client.get("/rover/status?rover_id=UNKNOWN-404")
    assert resp_status.status_code == 404
    assert "not found" in resp_status.json()["detail"].lower()

    resp_loc = client.get("/rover/location?rover_id=UNKNOWN-404")
    assert resp_loc.status_code == 404
    assert "not found" in resp_loc.json()["detail"].lower()


def test_get_status_and_location_no_telemetry(client):
    """
    Test GET /rover/status and GET /rover/location return 404 when rover exists but has no telemetry.
    """
    # Register a rover with no telemetry
    client.post("/rovers", json={"rover_id": "AR-EMPTY", "name": "Empty Rover", "status": "idle"})

    resp_status = client.get("/rover/status?rover_id=AR-EMPTY")
    assert resp_status.status_code == 404
    assert "no telemetry found" in resp_status.json()["detail"].lower()

    resp_loc = client.get("/rover/location?rover_id=AR-EMPTY")
    assert resp_loc.status_code == 404
    assert "no location found" in resp_loc.json()["detail"].lower()
