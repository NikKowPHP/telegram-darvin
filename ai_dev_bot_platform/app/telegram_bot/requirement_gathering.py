import logging
from enum import Enum, auto
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService
from app.services.orchestrator_service import OrchestratorService
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

class RequirementState(Enum):
    WAITING_FOR_PROJECT_NAME = auto()
    WAITING_FOR_PROJECT_DESCRIPTION = auto()
    WAITING_FOR_CONFIRMATION = auto()
    COMPLETED = auto()

async def start_requirement_gathering(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the requirement gathering process."""
    user_id = update.effective_user.id
    context.user_data["requirement_state"] = RequirementState.WAITING_FOR_PROJECT_NAME.value

    keyboard = [[ "Cancel" ]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Let's start by giving your project a name. This could be something like 'E-commerce Platform' or 'Task Management App':",
        reply_markup=reply_markup
    )

async def handle_project_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the project name input."""
    user_id = update.effective_user.id
    project_name = update.message.text

    if project_name.lower() == "cancel":
        await update.message.reply_text("Project creation cancelled.", reply_markup=ReplyKeyboardRemove())
        context.user_data.pop("requirement_state", None)
        return

    context.user_data["project_name"] = project_name
    context.user_data["requirement_state"] = RequirementState.WAITING_FOR_PROJECT_DESCRIPTION.value

    await update.message.reply_text(
        "Great! Now please describe your project in detail. Include:\n"
        "- The main purpose or goal\n"
        "- Target audience/users\n"
        "- Key features/functionality\n"
        "- Any specific technologies or frameworks you prefer\n\n"
        "Example: 'I want to build a task management app for small teams with features like task assignments, due dates, and progress tracking. Preferably using Python and React.'",
        reply_markup=ReplyKeyboardRemove()
    )

async def handle_project_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the project description input."""
    user_id = update.effective_user.id
    project_description = update.message.text

    context.user_data["project_description"] = project_description
    context.user_data["requirement_state"] = RequirementState.WAITING_FOR_CONFIRMATION.value

    project_summary = (
        f"Project Name: {context.user_data['project_name']}\n\n"
        f"Description: {project_description}\n\n"
        "Is this information correct?"
    )

    keyboard = [["Yes", "No"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        project_summary,
        reply_markup=reply_markup
    )

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the confirmation of project details."""
    user_id = update.effective_user.id
    confirmation = update.message.text

    if confirmation.lower() == "no":
        await update.message.reply_text(
            "Let's start over. What would you like to name your project?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["requirement_state"] = RequirementState.WAITING_FOR_PROJECT_NAME.value
        return

    if confirmation.lower() == "yes":
        # Save project to database
        db: Session = SessionLocal()
        try:
            project_service = ProjectService()
            project_data = ProjectCreate(
                name=context.user_data["project_name"],
                description=context.user_data["project_description"],
                user_id=user_id  # This should be the actual user ID from your auth system
            )
            project = project_service.create_project(db, project_data)
            project_id = project.id

            # Store project ID in context for future reference
            context.user_data["last_project_id"] = project_id

            await update.message.reply_text(
                f"Project '{project_data.name}' has been created successfully!",
                reply_markup=ReplyKeyboardRemove()
            )

            # Handoff to Orchestrator with the confirmed project description
            from app.services.orchestrator_service import get_orchestrator
            orchestrator = get_orchestrator(db)
            await orchestrator.start_planning_phase(project_id, project_data.description)

            # Reset state
            context.user_data["requirement_state"] = RequirementState.COMPLETED.value
        finally:
            db.close()
    else:
        await update.message.reply_text("Please respond with 'Yes' or 'No'.")

async def is_in_requirement_gathering(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if the user is in the requirement gathering process."""
    return "requirement_state" in context.user_data and (
        context.user_data["requirement_state"] != RequirementState.COMPLETED.value
    )