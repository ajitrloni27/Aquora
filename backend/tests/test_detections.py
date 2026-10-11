def test_create_and_get_detection(client):
    payload = {
        "label": "plastic_bottle",
        "confidence": 0.94,
        "depth": 2.1,
        "latitude": 15.3015,
        "longitude": 74.1270,
        "image_url": "https://example.com/snapshots/det_1.jpg",
    }
    # Create detection
    response = client.post("/detections", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["label"] == "plastic_bottle"
    assert data["confidence"] == 0.94
    detection_id = data["id"]

    # Fetch by ID
    get_resp = client.get(f"/detections/{detection_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == detection_id
    assert get_resp.json()["label"] == "plastic_bottle"

    # List detections
    list_resp = client.get("/detections")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert any(d["id"] == detection_id for d in items)

    # Filter detections by label
    filter_resp = client.get("/detections?label=plastic")
    assert filter_resp.status_code == 200
    assert len(filter_resp.json()) >= 1


def test_get_nonexistent_detection(client):
    response = client.get("/detections/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
