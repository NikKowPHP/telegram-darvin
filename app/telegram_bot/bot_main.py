from telegram.ext import Application, CommandHandler
from .handlers import credits_command

def main() -> None:
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()
    application.add_handler(CommandHandler("credits", credits_command))
    application.run_polling()

if __name__ == "__main__":
    main()