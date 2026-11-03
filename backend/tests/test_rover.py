from scripts.seed_rover import seed_rover


def test_seed_rover(db_session):
    """
    Test seed_rover function seeds AR-001 and does not duplicate if run again.
    """
    rover1 = seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)
    assert rover1.rover_id == "AR-001"
    assert rover1.status == "active"

    # Running again should return existing rover without duplicate key error
    rover2 = seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)
    assert rover2.id == rover1.id


def test_register_and_get_rover(client):
    """
    Test POST /rovers creates a new rover, and GET /rovers/{rover_id} retrieves it.
    """
    payload = {
        "rover_id": "AR-002",
        "name": "Aqua Rover Beta",
        "status": "idle",
    }
    response = client.post("/rovers", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["rover_id"] == "AR-002"
    assert data["name"] == "Aqua Rover Beta"
    assert data["status"] == "idle"
    assert "id" in data
    assert "created_at" in data

    # Retrieve specific rover
    get_resp = client.get("/rovers/AR-002")
    assert get_resp.status_code == 200
    assert get_resp.json()["rover_id"] == "AR-002"


def test_register_duplicate_rover(client):
    """
    Test POST /rovers with existing rover_id returns 409 Conflict.
    """
    payload = {
        "rover_id": "AR-003",
        "name": "Aqua Rover Gamma",
        "status": "idle",
    }
    resp1 = client.post("/rovers", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/rovers", json=payload)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"].lower()


def test_list_rovers(client):
    """
    Test GET /rovers returns all registered rovers.
    """
    client.post("/rovers", json={"rover_id": "AR-010", "name": "Rover Ten", "status": "active"})
    client.post("/rovers", json={"rover_id": "AR-011", "name": "Rover Eleven", "status": "idle"})

    resp = client.get("/rovers")
    assert resp.status_code == 200
    rovers = resp.json()
    assert isinstance(rovers, list)
    rover_ids = [r["rover_id"] for r in rovers]
    assert "AR-010" in rover_ids
    assert "AR-011" in rover_ids


def test_get_nonexistent_rover(client):
    """
    Test GET /rovers/{rover_id} for nonexistent rover returns 404 Not Found.
    """
    resp = client.get("/rovers/UNKNOWN-ROVER-999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
