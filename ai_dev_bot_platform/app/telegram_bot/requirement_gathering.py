# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Create requirement gathering handler
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters
from app.core.config import settings

async def start_requirement_gathering(update: Update, context: CallbackContext) -> None:
    """Start a new requirement gathering session."""
    await update.message.reply_text(
        "Let's gather your project requirements! Please describe what you need."
    )
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement requirement gathering initialization
    from app.services.conversation_service import create_conversation
    conversation = await create_conversation(
        user_id=update.effective_user.id,
        initial_message="Started requirement gathering session"
    )
    context.user_data['conversation_id'] = conversation.id
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END

async def handle_requirement_message(update: Update, context: CallbackContext) -> None:
    """Handle subsequent messages in requirement gathering."""
    user_message = update.message.text
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement conversation storage
    from app.services.conversation_service import add_message_to_conversation
    await add_message_to_conversation(
        conversation_id=context.user_data['conversation_id'],
        message=user_message,
        role="user"
    )
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
    await update.message.reply_text(
        f"Received your requirement: {user_message}\nPlease continue describing or type /done when finished."
    )

# Register handlers
def register_handlers(application):
    application.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        handle_requirement_message
    ))
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END
