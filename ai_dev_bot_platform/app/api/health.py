from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "OK"}

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_database)):
    try:
        # Simple database check
        db.execute("SELECT 1")
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )