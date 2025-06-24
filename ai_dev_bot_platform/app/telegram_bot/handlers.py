import asyncio
import logging
import uuid
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate
import json

from app.telegram_bot.requirement_gathering import (
    start_requirement_gathering,
    handle_project_name,
    handle_project_description,
    handle_confirmation,
    is_in_requirement_gathering,
)

logger = logging.getLogger(__name__)


def is_new_project_description(text: str) -> bool:
    """Heuristic to detect if a message is a new project description."""
    # It's a project description if it's long and doesn't start with a known command.
    is_long_enough = len(text.split()) > 5
    is_not_a_command = (
        not text.lower().strip().startswith(("implement task", "refine file", "/"))
    )
    return is_long_enough and is_not_a_command


# ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: Implement conversation starter command (/start)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    logger.info(f"User {user_tg.id} ({user_tg.username}) started the bot.")
    # ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: END

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
            # Start requirement gathering
            await start_requirement_gathering(update, context)
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
        "/credits - Check and purchase credits\n"
        "/status - Check project status and credits\n"
        "\n"
        "During development:\n"
        "- Describe your project to begin\n"
        "- Review and confirm requirements\n"
        "- Implement tasks as they're generated"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows current project status and credit balance"""
    user_tg = update.effective_user
    logger.info(f"User {user_tg.id} checking project status")

    db: Session = SessionLocal()
    try:
        user_service = UserService()
        user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
        if not user_db:
            await update.message.reply_text(
                "Please use /start first to initialize your account."
            )
            return

        project_id = context.user_data.get("last_project_id")
        status_message = f"Current credit balance: {user_db.credit_balance:.2f}\n\n"

        if project_id:
            from app.services.project_service import ProjectService

            project_service = ProjectService()
            project = project_service.get_project(db, uuid.UUID(project_id))
            if project:
                todo_lines = project.current_todo_markdown.split("\n")
                completed = len([line for line in todo_lines if "[x]" in line])
                remaining = len([line for line in todo_lines if "[ ]" in line])
                status_message += f"Active Project: {project.name}\n"
                status_message += f"Status: {project.status}\n"
                status_message += f"Tasks Completed: {completed}\n"
                status_message += f"Tasks Remaining: {remaining}"
            else:
                status_message += "No active project found"
        else:
            status_message += "No active project found"

        await update.message.reply_text(status_message)
    except Exception as e:
        logger.error(f"Error in status_command: {e}", exc_info=True)
        await update.message.reply_text("Sorry, couldn't retrieve your project status.")
    finally:
        db.close()


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


# ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: Implement message handlers for different requirement stages
# ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: END
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    # ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: END
    text = update.message.text

    logger.info(f"Received message from {user_tg.id}: {text}")

    # Check if user is in requirement gathering flow
    if await is_in_requirement_gathering(context):
        from app.telegram_bot.requirement_gathering import RequirementState

        state = context.user_data.get("requirement_state")

        if state == RequirementState.WAITING_FOR_PROJECT_NAME.value:
            await handle_project_name(update, context)
        elif state == RequirementState.WAITING_FOR_PROJECT_DESCRIPTION.value:
            await handle_project_description(update, context)
        elif state == RequirementState.WAITING_FOR_CONFIRMATION.value:
            await handle_confirmation(update, context)

        return

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

        # ROO-FIX-START: Replace the broken logic with the correct project creation and orchestration flow.

        # 1. Create a Project in the database
        project_service = ProjectService()
        # Since we don't have a title from a guided flow, we'll generate one.
        # The user's entire message becomes the description.
        project_in = ProjectCreate(
            title=f"New Project - {uuid.uuid4().hex[:6]}",
            description=text,
            user_id=user_db.id,
        )
        project = project_service.create_project(db, project_in, user_id=user_db.id)

        # 2. Store the *real* project ID in the user's context for future commands.
        context.user_data["last_project_id"] = str(project.id)
        logger.info(
            f"Created new project {project.id} for user {user_tg.id} and stored in context."
        )

        # 3. Send confirmation message
        await update.message.reply_text(
            "✅ Requirements received. The architect is now generating a plan..."
        )

        # 4. Handoff to the Orchestrator to start the planning phase.
        # This is the crucial step that was missing.
        # Note: This should be an async task so it doesn't block the bot.
        from app.services.orchestrator_service import get_orchestrator_service

        orchestrator = get_orchestrator_service(db)

        # Using asyncio.create_task to run the planning in the background
        # and immediately return control to the user.
        loop = asyncio.get_event_loop()
        loop.create_task(
            orchestrator.start_planning_phase(
                project_id=project.id,
                telegram_chat_id=update.effective_chat.id,
            )
        )
        # ROO-FIX-END

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

                from app.services.project_helpers import get_project_helpers

                project_helpers = get_project_helpers(db)
                # CLI runner will handle the actual processing
                response_data = {
                    "text": "Command received and queued for processing",
                    "zip_buffer": None,
                }

                await context.bot.send_message(
                    chat_id=user_tg.id,
                    text=response_data.get("text", "Task processing complete."),
                )
                # Check if more tasks exist and show next button
                from app.services.project_service import ProjectService

                project_service = ProjectService()
                project = project_service.get_project(db, uuid.UUID(project_id))
                if (
                    project
                    and len(project.current_todo_markdown.split("\n")) > task_index + 1
                ):
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                f"Implement Task {task_index + 1}",
                                callback_data=f"implement:{task_index + 1}",
                            )
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.send_message(
                        chat_id=user_tg.id,
                        text=f"Task {task_index} completed. Ready for next task?",
                        reply_markup=reply_markup,
                    )
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
