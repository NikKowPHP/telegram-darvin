import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session
from app.db.session import SessionLocal # For direct session if not using DI from framework
from app.services import user_service
from app.schemas.user import UserCreate
from app.services.payment_service import PaymentService
from app.core.config import settings

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    logger.info(f"User {user_tg.id} ({user_tg.username}) started the bot.")

    db: Session = SessionLocal() # Manual session management for handlers
    try:
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db:
            user_in = UserCreate(telegram_user_id=user_tg.id, username=user_tg.username)
            user_db = user_service.create_user(db, user_in=user_in)
            await update.message.reply_text(
                f"Welcome, {user_tg.first_name}! Your account has been created with initial credits: {user_db.credit_balance:.2f}."
            )
        else:
            await update.message.reply_text(
                f"Welcome back, {user_tg.first_name}! Your credit balance is: {user_db.credit_balance:.2f}."
            )
    except Exception as e:
        logger.error(f"Error in start_command for user {user_tg.id}: {e}", exc_info=True)
        await update.message.reply_text("Sorry, something went wrong while setting up your account.")
    finally:
        db.close()

    await update.message.reply_text(
        "I am your AI Development Assistant! Describe your project or use /help for commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start or restart the bot\n"
        "/help - Show this help message\n"
        "/credits - Check your credit balance\n"
        "/status - Check your project status and credits (TODO)\n"
        # Add more commands as they are implemented
    )

async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    logger.info(f"User {user_tg.id} checking credit balance")
    
    db: Session = SessionLocal()
    try:
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db:
            await update.message.reply_text("Please use /start first to initialize your account.")
            return
            
        keyboard = [
            [InlineKeyboardButton("Buy 100 Credits ($10)", callback_data='buy_100')],
            [InlineKeyboardButton("Buy 500 Credits ($45)", callback_data='buy_500')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Your current credit balance is: {user_db.credit_balance:.2f}.\n\n"
            "Purchase options will be available soon! Select an option to be notified:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in credits_command for user {user_tg.id}: {e}", exc_info=True)
        await update.message.reply_text("Sorry, couldn't retrieve your credit balance.")
    finally:
        db.close()

# Updated message handler with orchestrator integration
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    text = update.message.text
    logger.info(f"Received message from {user_tg.id}: {text}")

    db: Session = SessionLocal()
    try:
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db: # Should not happen if /start is always first, but good check
            await update.message.reply_text("Please use /start first to initialize your account.")
            return

        # Check credits (basic placeholder)
        if user_db.credit_balance <= 0:
            await update.message.reply_text("You have insufficient credits. Please /credits to add more. (TODO)")
            return

        from app.services.orchestrator_service import get_orchestrator
        orchestrator = get_orchestrator(db)
        response_data = await orchestrator.process_user_request(user=user_db, user_input=text)
        
        response_text = response_data.get('text')
        zip_buffer = response_data.get('zip_buffer')
        
        if response_text:
            await update.message.reply_text(response_text)

        if zip_buffer:
            project_title = response_data.get('project_title', 'project')
            file_name = f"{project_title.replace(' ', '_')}.zip"
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=zip_buffer,
                filename=file_name
            )

    except Exception as e:
        logger.error(f"Error in message_handler for user {user_tg.id}: {e}", exc_info=True)
        await update.message.reply_text("Sorry, an error occurred while processing your request.")
    finally:
        db.close()

# Add more handlers here (e.g., for project descriptions, other commands)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_tg = update.effective_user
    credit_package = query.data

    db: Session = SessionLocal()
    try:
        user_service = UserService()
        user_db = user_service.get_user_by_telegram_id(db, user_tg.id)
        if not user_db:
            await query.edit_message_text(text="Could not find your account. Please /start first.")
            return

        if settings.MOCK_STRIPE_PAYMENTS:
            # MOCK FLOW: Directly add credits
            updated_user = user_service.add_credits_after_purchase(db, user_id=user_db.id, credit_package=credit_package)
            if updated_user:
                await query.edit_message_text(
                    text=f"Success! Your MOCK purchase was processed. "
                         f"New balance: {updated_user.credit_balance:.2f}"
                )
            else:
                await query.edit_message_text(text="An error occurred during the mock purchase.")
        else:
            # LIVE FLOW: Generate a Stripe Checkout link
            payment_service = PaymentService()
            checkout_url = payment_service.create_checkout_session(user=user_db, credit_package=credit_package)
            
            if checkout_url:
                keyboard = [[InlineKeyboardButton("➡️ Proceed to Payment", url=checkout_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    text="Please complete your purchase using the link below:",
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text(text="Sorry, we could not create a payment link at this time.")
    
    except Exception as e:
        logger.error(f"Error in button_handler: {e}", exc_info=True)
        await query.edit_message_text(text="A server error occurred. Please try again later.")
    finally:
        db.close()