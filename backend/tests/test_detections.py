import pytest
from scripts.seed_rover import seed_rover


def test_create_detections_batch_success(client, db_session):
    """
    Test POST /detections creates multiple detection records in one transaction (201).
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)

    payload = {
        "rover_id": "AR-001",
        "timestamp": "2026-10-06T10:30:00Z",
        "detections": [
            {
                "class_name": "plastic_bottle",
                "confidence": 0.91,
                "bbox": [120.0, 80.0, 300.0, 250.0],
                "image_ref": "s3://bucket/det_1.jpg",
            },
            {
                "class_name": "plastic_bag",
                "confidence": 0.85,
                "bbox": [10.0, 20.0, 50.0, 60.0],
            },
        ],
    }

    response = client.post("/detections", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    assert data[0]["class_name"] == "plastic_bottle"
    assert data[0]["confidence"] == 0.91
    assert data[0]["bbox"] == [120.0, 80.0, 300.0, 250.0]
    assert data[0]["image_ref"] == "s3://bucket/det_1.jpg"
    assert "id" in data[0]

    assert data[1]["class_name"] == "plastic_bag"
    assert data[1]["confidence"] == 0.85
    assert data[1]["bbox"] == [10.0, 20.0, 50.0, 60.0]
    assert data[1]["image_ref"] is None
    assert "id" in data[1]


def test_create_detections_empty_list_422(client, db_session):
    """
    Test POST /detections rejects empty detections list with 422.
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)
    payload = {
        "rover_id": "AR-001",
        "timestamp": "2026-10-06T10:30:00Z",
        "detections": [],
    }
    response = client.post("/detections", json=payload)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "bad_bbox",
    [
        [10.0, 20.0, 30.0],  # only 3 coordinates
        [10.0, 20.0, 30.0, 40.0, 50.0],  # 5 coordinates
        [100.0, 50.0, 80.0, 150.0],  # x2 <= x1 (80 <= 100)
        [50.0, 100.0, 150.0, 80.0],  # y2 <= y1 (80 <= 100)
        [100.0, 100.0, 100.0, 200.0],  # x2 == x1
        [100.0, 100.0, 200.0, 100.0],  # y2 == y1
    ],
)
def test_create_detections_bad_bbox_422(client, db_session, bad_bbox):
    """
    Test POST /detections rejects malformed bounding boxes with 422.
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)
    payload = {
        "rover_id": "AR-001",
        "timestamp": "2026-10-06T10:30:00Z",
        "detections": [
            {
                "class_name": "plastic_bottle",
                "confidence": 0.90,
                "bbox": bad_bbox,
            }
        ],
    }
    response = client.post("/detections", json=payload)
    assert response.status_code == 422


def test_create_detections_unknown_rover_404(client):
    """
    Test POST /detections returns 404 when rover_id is unknown.
    """
    payload = {
        "rover_id": "UNKNOWN-999",
        "timestamp": "2026-10-06T10:30:00Z",
        "detections": [
            {
                "class_name": "plastic",
                "confidence": 0.95,
                "bbox": [10.0, 20.0, 100.0, 120.0],
            }
        ],
    }
    response = client.post("/detections", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_detections_ordering(client, db_session):
    """
    Test GET /detections returns detections ordered newest first (timestamp DESC).
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)

    # Insert older detection
    client.post(
        "/detections",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:00:00Z",
            "detections": [{"class_name": "old_bottle", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
        },
    )

    # Insert newer detection
    client.post(
        "/detections",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T12:00:00Z",
            "detections": [{"class_name": "new_bottle", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
        },
    )

    # Insert middle detection
    client.post(
        "/detections",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T11:00:00Z",
            "detections": [{"class_name": "mid_bottle", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
        },
    )

    response = client.get("/detections")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    assert items[0]["class_name"] == "new_bottle"
    assert items[1]["class_name"] == "mid_bottle"
    assert items[2]["class_name"] == "old_bottle"


def test_get_detections_filtering(client, db_session):
    """
    Test GET /detections filtering by rover_id, class_name, and min_confidence.
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)
    client.post("/rovers", json={"rover_id": "AR-002", "name": "Rover Two", "status": "active"})

    # AR-001 detections
    client.post(
        "/detections",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:00:00Z",
            "detections": [
                {"class_name": "plastic_bottle", "confidence": 0.95, "bbox": [0, 0, 10, 10]},
                {"class_name": "plastic_bag", "confidence": 0.60, "bbox": [0, 0, 10, 10]},
            ],
        },
    )

    # AR-002 detection
    client.post(
        "/detections",
        json={
            "rover_id": "AR-002",
            "timestamp": "2026-10-06T10:30:00Z",
            "detections": [
                {"class_name": "plastic_bottle", "confidence": 0.80, "bbox": [0, 0, 10, 10]},
            ],
        },
    )

    # Filter by rover_id
    r1 = client.get("/detections?rover_id=AR-001")
    assert r1.status_code == 200
    assert len(r1.json()) == 2
    assert all(d["rover_id"] == "AR-001" for d in r1.json())

    # Filter by class_name
    r2 = client.get("/detections?class_name=plastic_bag")
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    assert r2.json()[0]["class_name"] == "plastic_bag"

    # Filter by min_confidence
    r3 = client.get("/detections?min_confidence=0.85")
    assert r3.status_code == 200
    assert len(r3.json()) == 1
    assert r3.json()[0]["confidence"] == 0.95

    # Combined filters
    r4 = client.get("/detections?rover_id=AR-001&min_confidence=0.70")
    assert r4.status_code == 200
    assert len(r4.json()) == 1
    assert r4.json()[0]["class_name"] == "plastic_bottle"


def test_get_detections_pagination(client, db_session):
    """
    Test GET /detections pagination with limit and offset.
    """
    seed_rover("AR-001", "Aqua Rover Alpha", "active", db=db_session)

    items = [
        {"class_name": f"item_{i}", "confidence": 0.9, "bbox": [0, 0, 10, 10]}
        for i in range(5)
    ]
    client.post(
        "/detections",
        json={
            "rover_id": "AR-001",
            "timestamp": "2026-10-06T10:00:00Z",
            "detections": items,
        },
    )

    page1 = client.get("/detections?limit=2&offset=0")
    assert page1.status_code == 200
    assert len(page1.json()) == 2

    page2 = client.get("/detections?limit=2&offset=2")
    assert page2.status_code == 200
    assert len(page2.json()) == 2

    # Verify no overlap between page 1 and page 2
    page1_ids = [d["id"] for d in page1.json()]
    page2_ids = [d["id"] for d in page2.json()]
    assert set(page1_ids).isdisjoint(set(page2_ids))

    page3 = client.get("/detections?limit=2&offset=4")
    assert page3.status_code == 200
    assert len(page3.json()) == 1

    page4 = client.get("/detections?limit=2&offset=10")
    assert page4.status_code == 200
    assert len(page4.json()) == 0


def test_get_detections_pagination_validation(client):
    """
    Test GET /detections query parameter limits and constraints.
    """
    # limit < 1
    assert client.get("/detections?limit=0").status_code == 422
    # limit > 100
    assert client.get("/detections?limit=101").status_code == 422
    # offset < 0
    assert client.get("/detections?offset=-1").status_code == 422
    # min_confidence < 0 or > 1
    assert client.get("/detections?min_confidence=-0.1").status_code == 422
    assert client.get("/detections?min_confidence=1.1").status_code == 422
