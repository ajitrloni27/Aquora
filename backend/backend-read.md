# Aqua Rover Backend

FastAPI backend for the Aqua Rover project - an AI-powered water surface rover that detects floating waste.

## What It Does

- Receives AI detection data and rover telemetry from the Jetson edge device
- Validates and stores data in PostgreSQL
- Provides REST APIs for the React dashboard

## Tech Stack

- **Python** + **FastAPI**
- **PostgreSQL** + **SQLAlchemy**
- **Pydantic** for validation
- **Uvicorn** as ASGI server

## Setup

1. Clone the repo:
```bash
git clone <github.com/ajitrloni27/Aquora>
cd aqua-rover-backend
