# Aqua Rover Backend

A lightweight, reliable FastAPI service that powers the Aqua Rover water surface debris collection system.

---

## 1. What is Aqua Rover?

Aqua Rover is an AI-integrated semi-autonomous water-surface rover designed to detect and help collect floating waste, especially plastic. A camera on the rover feeds an onboard NVIDIA Jetson Orin Nano Super, which detects debris in real time. The rover cleans water bodies while streaming lightweight telemetry and detection data to shore.

---

## 2. What Does the Backend Do?

The backend is the middle layer between the rover and the user dashboard.

In plain words, the backend does four things:
1. **Receives data** from the rover's Jetson over HTTP JSON.
2. **Validates the data** using Pydantic to ensure coordinates, confidence scores, and bounding boxes are correct.
3. **Saves the data** in a PostgreSQL database using clean, transactional schemas.
4. **Serves the data** to the React dashboard when requested.

### What the Backend Does NOT Do:
* **It does NOT run the AI model.** YOLO inference runs locally on the Jetson Orin Nano Super.
* **It does NOT receive or stream video.** Video stays on the edge device to preserve bandwidth and battery. Only small JSON detection events are sent.
* **It does NOT render the user interface.** The web dashboard is rendered entirely by the React frontend.

---

## 3. Step-by-Step Example

Here is how data flows through the system when waste is found:

1. **Detection:** The camera on Aqua Rover spots a floating plastic bottle.
2. **Edge Inference:** YOLO runs on the Jetson and identifies the object with 91% confidence.
3. **HTTP POST:** The Jetson sends a JSON payload to `POST /detections`:

```json
{
  "rover_id": "AR-001",
  "timestamp": "2026-10-06T10:30:00Z",
  "detections": [
    {
      "class_name": "plastic",
      "confidence": 0.91,
      "bbox": [120.0, 80.0, 300.0, 250.0],
      "image_ref": "snapshots/AR-001_det_001.jpg"
    }
  ]
}
```

4. **Storage:** The backend validates coordinates and saves the record into PostgreSQL in one atomic transaction, responding with `201 Created`:

```json
[
  {
    "id": 14,
    "rover_id": "AR-001",
    "timestamp": "2026-10-06T10:30:00Z",
    "class_name": "plastic",
    "confidence": 0.91,
    "bbox": [120.0, 80.0, 300.0, 250.0],
    "image_ref": "snapshots/AR-001_det_001.jpg"
  }
]
```

5. **Dashboard Display:** The operator's React dashboard polls `GET /detections` and displays:
   > **"Plastic detected (91% confidence)"** with coordinates on the interactive map.

---

## 4. Architecture Diagram

```text
Sensors & Camera
       ↓
Jetson Orin Nano (YOLO AI)
       ↓
HTTP JSON (REST API)
       ↓
FastAPI Backend (Port 8000)
       ↓
PostgreSQL 16 Database (Port 5432)
       ↑
React Web Dashboard (HTTP Polling)
```

---

## 5. Technologies Used and Why

| Technology | Role | Why It Was Chosen |
| :--- | :--- | :--- |
| **Python 3.12** | Programming Language | Clean syntax, robust typing, wide edge and data tooling. |
| **FastAPI** | REST API Framework | High performance, automatic OpenAPI documentation (`/docs`), async-native. |
| **Pydantic v2** | Data Validation | Strict schema validation with clear error messages (422) for bad telemetry or bboxes. |
| **PostgreSQL 16** | Relational Database | Battle-tested reliability, JSON support, and fast time-series queries with compound indexes. |
| **SQLAlchemy 2.x** | Database ORM | Pythonic query builder with transaction management. |
| **Alembic** | Database Migrations | Version-controlled schema migrations for team collaboration. |
| **Uvicorn** | ASGI Web Server | Lightning-fast server for running FastAPI applications in production and development. |
| **pytest + httpx** | Automated Testing | Comprehensive test suite verifying all routes, status codes, and edge cases. |
| **Docker & Compose** | Container Packaging | Consistent local development and isolated PostgreSQL service. |
| **Postman** | API Testing | Standardized collection for testing endpoints without physical hardware. |
| **Git / GitHub** | Version Control | Feature branching, code reviews, and pull requests for every phase. |

---

## 6. Feature Status Table

| Feature / Endpoint | Status | Notes |
| :--- | :--- | :--- |
| `GET /health` | **Working** | Verifies database reachability via `SELECT 1` (200 / 503). |
| `POST /rovers` | **Working** | Registers new rovers with 409 duplicate detection. |
| `GET /rovers` | **Working** | Lists all registered rovers in the fleet. |
| `GET /rovers/{rover_id}` | **Working** | Retrieves rover metadata (404 if missing). |
| `POST /rover/telemetry` | **Working** | Validates telemetry & writes location in 1 transaction (201). |
| `GET /rover/status` | **Working** | Retrieves latest telemetry for a rover (default AR-001). |
| `GET /rover/location` | **Working** | Retrieves latest GPS position for a rover (default AR-001). |
| `POST /detections` | **Working** | Atomic batch ingestion with bounding box validation (201). |
| `GET /detections` | **Working** | Filter by rover, class, confidence; pagination; newest first. |
| Database Migrations | **Working** | Alembic migration `0001_initial_schema.py` defines all 4 tables. |
| Jetson Edge Simulator | **Working** | `scripts/simulate_jetson.py` with offline queue and retry. |
| Postman Collection | **Working** | `postman/aqua_rover.postman_collection.json` with variables. |
| Automated Test Suite | **Working** | 38 automated tests covering 200, 201, 404, 409, 422, 503. |
| Dockerfile (API Container) | **Planned** | Standalone production image to run in Phase 8. |
| Collection Statistics | **Planned** | Aggregated trash collection weight and counts. |
| Image Storage (AWS S3) | **Planned** | Uploading snapshot images to Amazon S3 buckets. |
| AWS Cloud Deployment | **Planned** | Hosting on AWS ECS / RDS with production domain. |
| Authentication & RBAC | **Planned** | API keys or JWT tokens for fleet operators. |

---

## 7. API Reference

All requests and responses use JSON.

### Health
* **`GET /health`**
  * **200 OK:** `{"status": "healthy", "project": "Aqua Rover Backend", "environment": "development", "timestamp": "...", "database": "connected"}`
  * **503 Service Unavailable:** `{"status": "degraded", "database": "disconnected", ...}`

### Rovers
* **`POST /rovers`**
  * Body: `{"rover_id": "AR-002", "name": "Aqua Rover Beta", "status": "idle"}`
  * **201 Created:** Returns created rover.
  * **409 Conflict:** If `rover_id` already exists.
  * **422 Unprocessable Entity:** Missing required fields.
* **`GET /rovers`**
  * **200 OK:** Returns array of rovers.
* **`GET /rovers/{rover_id}`**
  * **200 OK:** Returns rover details.
  * **404 Not Found:** If rover does not exist.

### Telemetry & Location
* **`POST /rover/telemetry`**
  * Body:
    ```json
    {
      "rover_id": "AR-001",
      "timestamp": "2026-10-06T10:30:00Z",
      "battery": 82.5,
      "speed": 0.8,
      "latitude": 12.345678,
      "longitude": 74.123456,
      "status": "moving",
      "temperature": 28.5,
      "signal": 95.0
    }
    ```
  * Note: `temperature` and `signal` are optional.
  * **201 Created:** Returns stored telemetry row. Writes both Telemetry and Location rows in one transaction.
  * **404 Not Found:** Unknown `rover_id`.
  * **422 Unprocessable Entity:** Battery outside 0–100, speed < 0, latitude outside -90 to 90, longitude outside -180 to 180.
* **`GET /rover/status`**
  * Query parameters: `rover_id` (optional, default `AR-001`).
  * **200 OK:** Returns latest telemetry object.
  * **404 Not Found:** Rover is unknown or has no recorded telemetry.
* **`GET /rover/location`**
  * Query parameters: `rover_id` (optional, default `AR-001`).
  * **200 OK:** Returns latest location object (`latitude`, `longitude`, `timestamp`).
  * **404 Not Found:** Rover is unknown or has no recorded location.

### Detections
* **`POST /detections`**
  * Body:
    ```json
    {
      "rover_id": "AR-001",
      "timestamp": "2026-10-06T10:30:00Z",
      "detections": [
        {
          "class_name": "plastic",
          "confidence": 0.91,
          "bbox": [120.0, 80.0, 300.0, 250.0],
          "image_ref": "snapshots/det_1.jpg"
        }
      ]
    }
    ```
  * **201 Created:** Returns array of saved detection objects.
  * **404 Not Found:** Unknown `rover_id`.
  * **422 Unprocessable Entity:** Empty `detections` list, or invalid bbox (must have 4 coordinates where $x_2 > x_1$ and $y_2 > y_1$).
* **`GET /detections`**
  * Query parameters:
    * `rover_id` (optional string): Filter by rover.
    * `class_name` (optional string): Filter by class name (e.g. `plastic`).
    * `min_confidence` (optional float between 0.0 and 1.0): Minimum confidence threshold.
    * `limit` (optional integer, default 50, max 100): Page size.
    * `offset` (optional integer, default 0): Number of records to skip.
  * **200 OK:** Returns list of detections ordered newest first (`timestamp DESC`).

---

## 8. How to Run It

### Prerequisites
* Python 3.10+
* Docker Desktop (or local PostgreSQL 16)
* Git

### Step-by-Step Setup
1. Clone the repository and enter the backend directory:
   ```bash
   git clone https://github.com/ajitrloni27/Aquora.git
   cd Aquora/backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
5. Start PostgreSQL using Docker:
   ```bash
   docker compose up -d postgres
   ```
6. Run database migrations:
   ```bash
   alembic upgrade head
   ```
7. Seed the initial rover (`AR-001`):
   ```bash
   python scripts/seed_rover.py
   ```
8. Start the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
9. Open API docs in your browser:
   * Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   * ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Running Automated Tests
Run the test suite using pytest:
```bash
pytest -v
```

---

## 9. Environment Variables

All settings are configured via `.env` in the `backend/` directory:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `Aqua Rover Backend` | Project title surfaced in docs and `/health`. |
| `ENVIRONMENT` | `development` | Deployment environment (`development`, `staging`, `production`). |
| `DEBUG` | `True` | Enables interactive OpenAPI docs (`/docs`) when `True`. |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/aqua_rover` | PostgreSQL connection string. |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173,...` | Comma-separated list of allowed frontend origins. |

---

## 10. How to Connect Other Parts to the Backend

### a) AI / Jetson (Detections)
The Jetson runs YOLO on the live camera stream. A lightweight Python script on the Jetson parses bounding boxes and sends JSON to `POST /detections`.

Because water bodies may have spotty Wi-Fi, the rover must buffer detections locally and retry when connectivity resumes.

**Copy-Paste Jetson Python Snippet:**
```python
import time
from collections import deque
from datetime import datetime, timezone
import requests

API_URL = "http://<BACKEND_LAN_IP>:8000/detections"
ROVER_ID = "AR-001"
offline_buffer = deque(maxlen=500)

def send_yolo_detections(yolo_results):
    items = []
    # Convert YOLO box results to pixel coordinates [x1, y1, x2, y2]
    for box in yolo_results:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        items.append({
            "class_name": box.cls_name,
            "confidence": round(float(box.conf), 2),
            "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
            "image_ref": None  # Optional snapshot filename
        })

    if not items:
        return

    payload = {
        "rover_id": ROVER_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detections": items
    }

    # Flush offline buffer first
    while offline_buffer:
        try:
            old_item = offline_buffer[0]
            r = requests.post(API_URL, json=old_item, timeout=3.0)
            if r.status_code == 201:
                offline_buffer.popleft()
            else:
                break
        except requests.RequestException:
            break

    # Send current detection
    try:
        r = requests.post(API_URL, json=payload, timeout=3.0)
        if r.status_code == 201:
            print("Detection logged successfully.")
        else:
            offline_buffer.append(payload)
    except requests.RequestException:
        print("Backend unreachable. Buffering detection locally.")
        offline_buffer.append(payload)
```

### b) Sensors / Hardware (Telemetry)
Sensors (GPS, battery voltage divider, water speed, motor temperature) are read on the Jetson or via an attached microcontroller (such as an Arduino or ESP32). A small script on the Jetson transmits these readings to `POST /rover/telemetry` every 3–5 seconds.

> **Note:** Sensor hardware reading code is owned by the hardware and robotics team. The backend only receives and validates the values.

**Copy-Paste Telemetry Script:**
```python
import time
from datetime import datetime, timezone
import requests

API_URL = "http://<BACKEND_LAN_IP>:8000/rover/telemetry"

def send_telemetry():
    payload = {
        "rover_id": "AR-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery": 87.5,        # 0.0 - 100.0 percent
        "speed": 0.85,          # meters per second (>= 0.0)
        "latitude": 15.301540,  # GPS latitude (-90.0 to 90.0)
        "longitude": 74.127020, # GPS longitude (-180.0 to 180.0)
        "status": "moving",     # idle, moving, collecting
        "temperature": 29.1,    # optional, Celsius
        "signal": 94.0          # optional, percentage
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=3.0)
        if resp.status_code == 201:
            print("Telemetry updated.")
    except requests.RequestException as e:
        print("Could not reach backend:", e)

# Send every 3 seconds
if __name__ == "__main__":
    while True:
        send_telemetry()
        time.sleep(3)
```

### c) Frontend (React Dashboard)
The React dashboard polls the backend every 2–5 seconds over HTTP (no WebSockets needed).

* **Endpoints to call:**
  * `GET /rover/status?rover_id=AR-001`: Shows current battery, speed, and state.
  * `GET /rover/location?rover_id=AR-001`: Plots rover pin on the live map.
  * `GET /detections?rover_id=AR-001&limit=20`: Shows recent debris list.
* **Frontend configuration:**
  * Add the backend URL to the React `.env`: `VITE_API_URL=http://localhost:8000`
  * Add the React frontend address (e.g. `http://localhost:5173`) to `CORS_ORIGINS` in backend `.env`.

**React fetch() Example:**
```javascript
// Fetch latest rover telemetry
async function fetchRoverStatus() {
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${API_URL}/rover/status?rover_id=AR-001`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    console.log(`Battery: ${data.battery}%, Speed: ${data.speed} m/s`);
  } catch (err) {
    console.error("Failed to fetch rover status:", err);
  }
}
```

### d) Network Setup
* **Local Wi-Fi Testing:** When testing with physical hardware on the same Wi-Fi network, devices cannot connect to `localhost`. Run Uvicorn with `--host 0.0.0.0` and point the Jetson and frontend to the host computer's local IP (e.g. `http://192.168.1.50:8000`). Make sure port 8000 is open in the firewall.
* **Vercel / Cloud Frontend:** If the React dashboard is hosted on Vercel, the backend needs a public HTTPS URL (e.g. via Cloudflare Tunnels or ngrok for development, or an AWS EC2 instance later). Add the Vercel domain to `CORS_ORIGINS`.
* **Security Notice:** There is no authentication or token gating implemented yet. Only use mock or non-sensitive data during open network testing.

### e) Testing Without Physical Hardware
You can test the entire stack right now without hardware:
1. Run the edge simulator:
   ```bash
   python scripts/simulate_jetson.py --base-url http://localhost:8000 --rover-id AR-001
   ```
2. Or import [postman/aqua_rover.postman_collection.json](postman/aqua_rover.postman_collection.json) into Postman to send requests manually.

---

## 11. Project Structure

```text
backend/
├── alembic/                      # Database migration configuration
│   ├── versions/                 # Version-controlled schema migrations
│   │   └── 0001_initial_schema.py# Creates rovers, telemetry, locations, detections
│   ├── env.py                    # Alembic migration environment
│   └── script.py.mako            # Migration template
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── detections.py     # POST /detections, GET /detections
│   │   │   ├── health.py         # GET /health
│   │   │   └── rover.py          # /rovers CRUD and /rover/status, /location, /telemetry
│   │   └── router.py             # Mounts all API route modules
│   ├── core/
│   │   └── config.py             # App settings loaded from .env
│   ├── db/
│   │   ├── base.py               # DeclarativeBase class
│   │   └── session.py            # Engine, sessionmaker, and get_db dependency
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── detection.py          # Detection table definition
│   │   ├── location.py           # Location table definition
│   │   ├── rover.py              # Rover table definition
│   │   └── telemetry.py          # Telemetry table definition
│   ├── schemas/                  # Pydantic v2 validation models
│   │   ├── detection.py          # DetectionItem, DetectionsBatchCreate, DetectionResponse
│   │   ├── health.py             # HealthResponse schema
│   │   ├── location.py           # LocationResponse schema
│   │   ├── rover.py              # RoverCreate, RoverResponse schemas
│   │   └── telemetry.py          # TelemetryCreate, TelemetryResponse schemas
│   ├── services/                 # Core business and database logic
│   │   ├── detection_service.py  # Ingestion & filtering for detections
│   │   ├── health_service.py     # Database connectivity check (SELECT 1)
│   │   └── rover_service.py      # Telemetry, location, and rover CRUD logic
│   └── main.py                   # FastAPI app entry point and CORS setup
├── postman/
│   └── aqua_rover.postman_collection.json # Full Postman API test collection
├── scripts/
│   ├── seed_rover.py             # Idempotently seeds default rover AR-001
│   └── simulate_jetson.py        # Edge device telemetry & YOLO simulator
├── tests/                        # Automated pytest suite
│   ├── conftest.py               # Fixtures with in-memory SQLite and mock db
│   ├── test_detections.py        # Detection batch, validation, and filter tests
│   ├── test_health.py            # /health endpoint and DB disconnect tests
│   ├── test_rover.py             # /rovers CRUD and duplicate tests
│   ├── test_status_codes.py      # Explicit 200, 201, 404, 409, 422, 503 test suite
│   └── test_telemetry.py         # Dual-write telemetry & location tests
├── .env.example                  # Environment variable reference
├── .gitignore                    # Ignored files (venv, env, cache)
├── alembic.ini                   # Alembic configuration file
├── docker-compose.yml            # Multi-container orchestration (Postgres + API)
└── requirements.txt              # Pinned Python project dependencies
```

---

## 12. Data Model

The database schema is organized into four tables:

```text
┌─────────────────────────┐         ┌─────────────────────────────────┐
│         rovers          │         │            telemetry            │
├─────────────────────────┤         ├─────────────────────────────────┤
│ id (PK, Integer)        │1       *│ id (PK, Integer)                │
│ rover_id (Unique, String)────────<│ rover_id (FK -> rovers.rover_id)│
│ name (String)           │         │ timestamp (DateTime UTC)        │
│ status (String)         │         │ battery (Float, 0.0 - 100.0)    │
│ created_at (DateTime)   │         │ speed (Float, >= 0.0)           │
└────────────┬────────────┘         │ status (String)                 │
             │                      │ temperature (Float, Nullable)   │
             │                      │ signal (Float, Nullable)        │
             │                      └─────────────────────────────────┘
             │
             │1                     ┌─────────────────────────────────┐
             ├─────────────────────<│            locations            │
             │                     *├─────────────────────────────────┤
             │                      │ id (PK, Integer)                │
             │                      │ rover_id (FK -> rovers.rover_id)│
             │                      │ timestamp (DateTime UTC)        │
             │                      │ latitude (Float, -90.0..90.0)   │
             │                      │ longitude (Float, -180..180)    │
             │                      └─────────────────────────────────┘
             │
             │1                     ┌─────────────────────────────────┐
             └─────────────────────<│           detections            │
                                   *├─────────────────────────────────┤
                                    │ id (PK, Integer)                │
                                    │ rover_id (FK -> rovers.rover_id)│
                                    │ timestamp (DateTime UTC)        │
                                    │ class_name (String, Indexed)    │
                                    │ confidence (Float, 0.0 - 1.0)   │
                                    │ bbox (JSON [x1, y1, x2, y2])    │
                                    │ image_ref (String, Nullable)    │
                                    └─────────────────────────────────┘
```

---

## 13. Team Roles and Ownership

| Team Member | Domain | Responsibilities | Contracts Agreed With Backend |
| :--- | :--- | :--- | :--- |
| **Backend Engineer (ME)** | FastAPI Backend & PostgreSQL | REST API endpoints, Pydantic validation, database transactions, migrations, and automated tests. | Owns the API contract and database schemas. |
| **AI Engineer 1 & 2** | YOLO Inference & Training | Edge model optimization on Jetson Orin Nano, model training, and labeling floating plastic waste. | Agrees on `POST /detections` JSON shape (classes, confidence, bbox). |
| **Frontend Engineer** | React Web Dashboard | Operator UI, live map visualization, polling metrics, and telemetry displays. | Agrees on query params and response models for `/rover/*` and `/detections`. |
| **CTO** | Architecture & Cloud/DevOps | Overall system architecture, AWS infrastructure, hardware sensors, and PR reviews. | Agrees on deployment pipelines and hardware sensor data formats. |

---

## 14. Roadmap

Planned future enhancements beyond current scope:
1. **Production Dockerfile:** Multi-stage container build for the FastAPI application (Phase 8).
2. **Amazon S3 Integration:** Secure presigned URL generation and automated image snapshot uploads.
3. **Analytics & Aggregations:** Summary endpoints (`GET /stats/summary`) for total trash collected and area patrolled.
4. **Authentication:** Fleet API key authentication for rovers and role-based access for dashboard operators.
5. **AWS Deployment:** Terraform / CDK deployment scripts targeting AWS ECS Fargate and AWS RDS PostgreSQL.
