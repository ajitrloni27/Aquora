#!/bin/sh
set -e

echo "[Aqua Rover] Running database migrations..."
alembic upgrade head

echo "[Aqua Rover] Seeding default rover AR-001..."
python scripts/seed_rover.py

echo "[Aqua Rover] Starting Uvicorn ASGI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
