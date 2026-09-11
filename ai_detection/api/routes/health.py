# ai_detection/api/routes/health.py
"""Health check endpoint for FastAPI backend."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health check")
async def health_check():
    return {"status": "ok"}
