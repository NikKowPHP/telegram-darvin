import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session
from app.db.session import (
    SessionLocal,
)  # For direct session if not using DI from framework
from app.services.user_service import UserService  # CORRECTED IMPORT
from app.schemas.user import UserCreate
from app.services.payment_service import PaymentService
from app.core.config import settings
import json

logger = logging.getLogger(__name__)


def is_new_project_description(text: str) -> bool:
    """Heuristic to detect if a message is a new project description."""
    # It's a project description if it's long and doesn't start with a known command.
    is_long_enough = len(text.split()) > 5
    is_not_a_command = (
        not text.lower().strip().startswith(("implement task", "refine file", "/"))
    )
    return is_long_enough and is_not_a_command


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    logger.info(f"User {user_tg.id} ({user_tg.username}) started the bot.")

    db: Session = SessionLocal()  # Manual session management for handlers
    try:
        user_service = UserService()  # ADDED: Instantiate the service
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
        logger.error(
            f"Error in start_command for user {user_tg.id}: {e}", exc_info=True
        )
        await update.message.reply_text(
            "Sorry, something went wrong while setting up your account."
        )
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
        "/buy_credits - Purchase additional credits\n"
        # Add more commands as they are implemented
    )


async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    logger.info(f"User {user_tg.id} checking credit balance")

    db: Session = SessionLocal()
    try:
        user_service = UserService()  # ADDED: Instantiate the service
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db:
            await update.message.reply_text(
                "Please use /start first to initialize your account."
            )
            return

        keyboard = [
            [InlineKeyboardButton("Buy 100 Credits ($10)", callback_data="buy_100")],
            [InlineKeyboardButton("Buy 500 Credits ($45)", callback_data="buy_500")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Your current credit balance is: {user_db.credit_balance:.2f}.\n\n"
            "Purchase options will be available soon! Select an option to be notified:",
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(
            f"Error in credits_command for user {user_tg.id}: {e}", exc_info=True
        )
        await update.message.reply_text("Sorry, couldn't retrieve your credit balance.")
    finally:
        db.close()


# In app/telegram_bot/handlers.py


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    text = update.message.text

    logger.info(f"Received message from {user_tg.id}: {text}")

    db: Session = SessionLocal()
    try:
        user_service = UserService()
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db:
            await update.message.reply_text(
                "Please use /start first to initialize your account."
            )
            return

        if user_db.credit_balance <= 0:
            await update.message.reply_text(
                "You have insufficient credits. Please /credits to add more."
            )
            return

        # Send an immediate acknowledgement for long-running tasks
        if is_new_project_description(text):
            await update.message.reply_text(
                "Thanks! I'm analyzing your project requirements and creating an initial plan. This might take a moment..."
            )
        elif text.lower().strip().startswith("implement task"):
            await update.message.reply_text(
                "Got it. Working on that task now. This may take a minute..."
            )

        from app.services.orchestrator_service import get_orchestrator

        orchestrator = get_orchestrator(db)
        response_data = await orchestrator.process_user_request(
            user=user_db, user_input=text
        )

        response_text = response_data.get("text")
        zip_buffer = response_data.get("zip_buffer")
        reply_markup = response_data.get("reply_markup")
        project_id = response_data.get("project_id")

        # If a new project was created, store its ID in the user's context data
        if project_id and is_new_project_description(text):
            context.user_data["last_project_id"] = project_id
            logger.info(f"Stored last_project_id for user {user_tg.id}: {project_id}")

        if response_text:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=response_text,
                reply_markup=reply_markup,
            )

        if zip_buffer:
            project_title = response_data.get("project_title", "project")
            file_name = f"{project_title.replace(' ', '_')}.zip"
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=zip_buffer,
                filename=file_name,
            )

    except Exception as e:
        logger.error(
            f"Error in message_handler for user {user_tg.id}: {e}", exc_info=True
        )
        if not context.bot_data.get(f"replied_to_{update.message.message_id}", False):
            await update.message.reply_text(
                "Sorry, an error occurred while processing your request."
            )
    finally:
        db.close()


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_tg = update.effective_user

    # Try to parse the callback data using the new 'action:value' format
    try:
        parts = query.data.split(":")
        action = parts[0]

        if action == "implement":
            task_index = int(parts[1])

            project_id = context.user_data.get("last_project_id")
            if not project_id:
                await query.edit_message_text(
                    text="Error: I've lost track of the project. Please create a new one."
                )
                return

            await query.edit_message_text(
                text=f"▶️ Working on Task {task_index} for project {project_id[:8]}...\n\nThis may take a minute or two."
            )

            command_string = f"implement task {task_index} of project {project_id}"

            db: Session = SessionLocal()
            try:
                user_service = UserService()
                user_db = user_service.get_user_by_telegram_id(db, user_tg.id)
                if not user_db:
                    await context.bot.send_message(
                        chat_id=user_tg.id,
                        text="Error: Could not find your user account.",
                    )
                    return

                from app.services.orchestrator_service import get_orchestrator

                orchestrator = get_orchestrator(db)
                response_data = await orchestrator.process_user_request(
                    user=user_db, user_input=command_string
                )

                await context.bot.send_message(
                    chat_id=user_tg.id,
                    text=response_data.get("text", "Task processing complete."),
                )
                # TODO: Here you could add logic to send the next button, e.g., "Implement Task 2"
            finally:
                db.close()
            return

    except (IndexError, ValueError):
        # Data is not in 'action:value' format, fall through to credit logic
        pass
    except Exception as e:
        logger.error(f"Error in button_handler action processing: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=user_tg.id, text="An error occurred while processing that action."
        )
        return

    # Fallback to existing credit purchase logic
    credit_package = query.data
    db: Session = SessionLocal()
    try:
        user_service = UserService()
        user_db = user_service.get_user_by_telegram_id(db, user_tg.id)
        if not user_db:
            await query.edit_message_text(
                text="Could not find your account. Please /start first."
            )
            return

        if settings.MOCK_STRIPE_PAYMENTS:
            updated_user = user_service.add_credits_after_purchase(
                db, user_id=user_db.id, credit_package=credit_package
            )
            if updated_user:
                await query.edit_message_text(
                    text=f"Success! Your MOCK purchase was processed. New balance: {updated_user.credit_balance:.2f}"
                )
            else:
                await query.edit_message_text(
                    text="An error occurred during the mock purchase."
                )
        else:
            payment_service = PaymentService()
            checkout_url = payment_service.create_checkout_session(
                user=user_db, credit_package=credit_package
            )

            if checkout_url:
                keyboard = [
                    [InlineKeyboardButton("➡️ Proceed to Payment", url=checkout_url)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    text="Please complete your purchase using the link below:",
                    reply_markup=reply_markup,
                )
            else:
                await query.edit_message_text(
                    text="Sorry, we could not create a payment link at this time."
                )

    except Exception as e:
        logger.error(f"Error in button_handler: {e}", exc_info=True)
        await query.edit_message_text(
            text="We're experiencing issues with our payment system. Please try your purchase again in a few minutes."
        )
    finally:
        db.close()

async def buy_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    logger.info(f"User {user_tg.id} requesting to buy credits")
    
    db: Session = SessionLocal()
    try:
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db:
            await update.message.reply_text("Please use /start first to initialize your account.")
            return
            
        await update.message.reply_text(
            "Credit purchase functionality is coming soon!\n\n"
            "For now, please contact support to add credits to your account."
        )
    except Exception as e:
        logger.error(f"Error in buy_credits_command for user {user_tg.id}: {e}", exc_info=True)
        await update.message.reply_text("Sorry, couldn't process your credit purchase request.")
    finally:
        db.close()
