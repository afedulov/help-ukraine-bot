"""put module docstring here"""

from telegram.ext import (
    Updater,
    MessageHandler,
    InlineQueryHandler,
    Filters,
)

import commands
import education
import finance
import general_information
import medical
from config import (
    APP_NAME,
    TOKEN,
    PORT,
)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    commands.add_commands(dispatcher)

    education_commands = education.register_commands(dispatcher)
    finance_commands = finance.register_commands(dispatcher)
    general_information_commands = general_information.register_commands(dispatcher)
    medical_commands = medical.register_commands(dispatcher)

    command_list = education_commands + finance_commands + general_information_commands + medical_commands + commands.get_command_list()
    command_list.sort(key=lambda x: x.command)

    updater.bot.set_my_commands(command_list)

    # Messages
    dispatcher.add_handler(MessageHandler(Filters.all, commands.delete_greetings))

    # Inlines
    dispatcher.add_handler(InlineQueryHandler(commands.find_articles_command))

    if APP_NAME == "TESTING":
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
        updater.bot.setWebhook(f"https://{APP_NAME}.herokuapp.com/{TOKEN}")

    updater.idle()


if __name__ == "__main__":
    main()
