# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Create requirement gathering handler
import logging
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters
from app.core.config import settings
from app.services.conversation_service import create_conversation, get_conversation
from telegram.ext import CommandHandler

async def start_requirement_gathering(update: Update, context: CallbackContext) -> None:
    """Start a new requirement gathering session with /startrequirements command."""
    try:
        await update.message.reply_text(
            "Let's gather your project requirements! Please describe what you need.\n"
            "Type /done when you finish describing your requirements."
        )
        conversation = await create_conversation(
            user_id=update.effective_user.id,
            initial_message="Started requirement gathering session"
        )
        context.user_data['conversation_id'] = conversation.id
        context.user_data['requirement_gathering'] = True
    except Exception as e:
        logging.error(f"Failed to start requirement gathering: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Failed to start requirement gathering session. Please try again later."
        )

async def handle_requirement_message(update: Update, context: CallbackContext) -> None:
    """Handle subsequent messages in requirement gathering and extract requirements."""
    user_message = update.message.text
    
    # Extract key requirements from message
    requirements = {
        "raw": user_message,
        "features": [],
        "technologies": [],
        "constraints": []
    }
    
    # Simple pattern matching for requirements extraction
    if "need" in user_message.lower():
        requirements['features'].append(user_message)
    if "using" in user_message.lower():
        requirements['technologies'].append(user_message.split("using")[-1].strip())
    if "must" in user_message.lower() or "require" in user_message.lower():
        requirements['constraints'].append(user_message)
    
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement conversation storage
    from app.services.conversation_service import add_message_to_conversation
    await add_message_to_conversation(
        conversation_id=context.user_data['conversation_id'],
        message=user_message,
        role="user",
        requirements=requirements  # Store structured requirements
    )
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
    
    # Provide more helpful feedback
    response = f"✅ Recorded requirement: {user_message}"
    if requirements['features']:
        response += f"\n\nDetected features:\n- " + "\n- ".join(requirements['features'])
    await update.message.reply_text(response + "\n\nPlease continue or type /done when finished.")

async def finish_requirement_gathering(update: Update, context: CallbackContext) -> None:
    """Finalize the requirement gathering session with /done command."""
    if 'requirement_gathering' not in context.user_data:
        await update.message.reply_text("No active requirement gathering session.")
        return
    
    try:
        conversation = await get_conversation(context.user_data['conversation_id'])
        await update.message.reply_text(
            f"Thank you! We've recorded {len(conversation.messages)} requirements.\n"
            "Your project will be processed shortly."
        )
        del context.user_data['requirement_gathering']
        del context.user_data['conversation_id']
    except Exception as e:
        logging.error(f"Failed to finalize requirement gathering: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Failed to finalize requirement gathering. Please contact support."
        )

# Register handlers
def register_handlers(application):
    application.add_handler(CommandHandler("startrequirements", start_requirement_gathering))
    application.add_handler(CommandHandler("done", finish_requirement_gathering))
    application.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        handle_requirement_message
    ))
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END
