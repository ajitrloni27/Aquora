def test_get_initial_rover_status(client):
    response = client.get("/rover/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["idle", "active", "returning", "error"]
    assert "battery_level" in data
    assert "depth" in data
    assert "temperature" in data
    assert "id" in data


def test_post_rover_status(client):
    payload = {
        "battery_level": 88.5,
        "temperature": 23.2,
        "depth": 3.4,
        "speed": 1.2,
        "status": "active",
        "latitude": 15.3010,
        "longitude": 74.1265,
    }
    response = client.post("/rover/status", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["battery_level"] == 88.5
    assert data["status"] == "active"
    assert data["depth"] == 3.4
    assert data["id"] is not None

    # Check that GET /rover/status now reflects this latest status
    latest_resp = client.get("/rover/status")
    assert latest_resp.status_code == 200
    assert latest_resp.json()["id"] == data["id"]
    assert latest_resp.json()["status"] == "active"


def test_get_rover_status_history(client):
    # Post a telemetry record first
    client.post("/rover/status", json={
        "battery_level": 95.0,
        "temperature": 24.0,
        "depth": 1.5,
        "speed": 0.5,
        "status": "active",
    })

    response = client.get("/rover/status/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
