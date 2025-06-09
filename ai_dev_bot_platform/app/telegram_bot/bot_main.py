import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.core.config import settings
from app.telegram_bot.handlers import start_command, help_command, credits_command, message_handler, button_handler

logger = logging.getLogger(__name__)

async def run_bot():
    logger.info("Starting Telegram bot...")
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("credits", credits_command))
    # Add more command handlers here

    # Register message handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Telegram bot polling...")
    await application.run_polling()
