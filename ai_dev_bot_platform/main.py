import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logging_config import setup_logging
from app.telegram_bot.bot_main import run_bot
from app.api.endpoints import stripe_webhooks
from app.api.health import router as health_router

# Setup logging at the application's entry point
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    print("Application startup: Starting Telegram bot in background...")
    loop = asyncio.get_event_loop()
    bot_task = loop.create_task(run_bot())
    yield
    # This code runs on shutdown
    print("Application shutdown: Stopping Telegram bot...")
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        print("Bot task successfully cancelled.")

app = FastAPI(title="AI Development Assistant API", lifespan=lifespan)
app.include_router(stripe_webhooks.router, prefix="/api/v1", tags=["Stripe"])
app.include_router(health_router, prefix="/health", tags=["health"])

@app.get("/")
async def root():
    return {"message": "AI Development Assistant API is running and bot is active!"}



@app.post("/admin/set-credits/{telegram_user_id}")
async def set_user_credits(
    telegram_user_id: int,
    credits: float,
    db: Session = Depends(get_db)
):
    """
    Temporary admin endpoint to set a user's credit balance.
    """
    from decimal import Decimal
    user_service = UserService()
    user = user_service.get_user_by_telegram_id(db, telegram_user_id)
    if not user:
        return {"error": "User not found"}

    user.credit_balance = Decimal(str(credits))
    db.commit()
    db.refresh(user)

    return {"message": f"Successfully set credits for user {telegram_user_id} to {user.credit_balance}"}