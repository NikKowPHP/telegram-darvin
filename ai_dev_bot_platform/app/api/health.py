from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import httpx
from app.core.config import settings
import logging

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


@router.get("/telegram")
async def telegram_connectivity_check():
    """
    Checks if the application can connect to the Telegram Bot API.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(
            status_code=500, detail="TELEGRAM_BOT_TOKEN is not configured."
        )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    return {
                        "status": "OK",
                        "bot_username": bot_info["result"]["username"],
                    }

            # If we reach here, something is wrong
            error_detail = response.json().get("description", "Unknown error")
            logger.error(
                f"Telegram API check failed: {response.status_code} - {error_detail}"
            )
            raise HTTPException(
                status_code=503, detail=f"Telegram API error: {error_detail}"
            )

    except httpx.RequestError as e:
        logger.error(f"Telegram API check failed: Could not connect to Telegram: {e}")
        raise HTTPException(
            status_code=503, detail=f"Could not connect to Telegram API: {str(e)}"
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during Telegram health check: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
