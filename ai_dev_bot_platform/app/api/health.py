from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "OK"}

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        # Simple database check
        db.execute(text("SELECT 1"))
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )