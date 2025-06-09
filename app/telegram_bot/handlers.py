from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services import user_service

async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    db: Session = SessionLocal()
    try:
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db:
            await update.message.reply_text("Please use /start first.")
            return
        await update.message.reply_text(
            f"Your current credit balance is: {user_db.credit_balance:.2f}.\n"
            "Purchase options will be available soon!"
        )
    finally:
        db.close()