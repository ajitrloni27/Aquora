from fastapi import APIRouter
from app.api.routes import rover, detections

api_router = APIRouter()
api_router.include_router(rover.router)
api_router.include_router(detections.router)
