"""put module docstring here"""
import configparser
from os import environ as env
import logging
from functools import wraps
from typing import Tuple
from telegram import (
    Update,
    Bot,
    BotCommand,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    JobQueue,
    Job,
)
from telegram.error import BadRequest
from telegram.utils.helpers import effective_message_type

import commands
from guidebook import Guidebook

from src.reminders import reminder

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("settings.env")

try:
    APP_NAME = env["APP_NAME"]
    TOKEN = env["TOKEN"]
except KeyError:
    APP_NAME = config.get("DEVELOPMENT", "APP_NAME")
    TOKEN = config.get("DEVELOPMENT", "TOKEN")

PORT = int(env.get("PORT", 5000))
THUMB_URL = env.get(
    "THUMB_URL",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/2560px-Flag_of_Ukraine.svg.png",
)


ADMIN_ONLY_CHAT_IDS = [-1001723117571, -735136184]

BERLIN_HELPS_UKRAIN_CHAT_ID = [-1001589772550, -1001790676165, -735136184]

guidebook = Guidebook()


# Permissions
def restricted(func):
    """A decorator that limits the access to commands only for admins"""

    @wraps(func)
    def wrapped(bot: Bot, context: CallbackContext, *args, **kwargs):
        user_id = context.effective_user.id
        chat_id = context.effective_chat.id
        admins = [u.user.id for u in bot.get_chat_administrators(chat_id)]

        if user_id not in admins:
            logger.warning("Non admin attempts to access a restricted function")
            return

        logger.info("Restricted function permission granted")
        return func(bot, context, *args, **kwargs)

    return wrapped


def restricted_general(func):
    """A decorator that limits the access to commands only for admins"""

    @wraps(func)
    def wrapped(bot: Bot, context: CallbackContext, *args, **kwargs):
        user_id = context.effective_user.id
        chat_id = context.effective_chat.id
        chat = bot.get_chat(chat_id)
        if chat.type == "group":
            admins = [u.user.id for u in bot.get_chat_administrators(chat_id)]

            if chat_id in ADMIN_ONLY_CHAT_IDS:
                if user_id not in admins:
                    logger.warning("Non admin attempts to access a restricted function")
                    message_id = context.message.message_id
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    return

        logger.info("Restricted function permission granted")
        return func(bot, context, *args, **kwargs)

    return wrapped


def delete_greetings(bot: Bot, update: Update) -> None:
    """Echo the user message."""
    message = update.message
    if message:
        msg_type = effective_message_type(message)
        logger.debug("Handling type is %s", msg_type)
        if effective_message_type(message) in [
            "new_chat_members",
            "left_chat_member",
        ]:
            bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)


@restricted
def start_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """start_timer"""
    message = update.message
    chat_id = message.chat_id
    command_message_id = message.message_id
    if chat_id in BERLIN_HELPS_UKRAIN_CHAT_ID:
        reminder(bot, update, job_queue)
    try:
        bot.delete_message(chat_id=chat_id, message_id=command_message_id)
    except BadRequest:
        logger.info("Command was already deleted %s", command_message_id)


@restricted
def admins_only(bot: Bot, update: Update):
    chat_id = update.message.chat_id
    ADMIN_ONLY_CHAT_IDS.append(chat_id)
    bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)


@restricted
def admins_only_revert(bot: Bot, update: Update):
    chat_id = update.message.chat_id
    ADMIN_ONLY_CHAT_IDS.remove(chat_id)
    bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)


@restricted
def stop_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """stop_timer"""
    chat_id = update.message.chat_id

    #  Stop already existing jobs
    jobs: Tuple[Job] = job_queue.get_jobs_by_name(chat_id)
    for job in jobs:
        bot.send_message(chat_id=chat_id, text="I'm stopping sending the reminders.")
        job.enabled = False

    logger.info("Stopped reminders in channel %s", chat_id)


def reply_to_message(bot, update, reply, disable_web_page_preview=True):
    message = update.message
    chat_id = message.chat_id
    command_message_id = message.message_id

    if message.reply_to_message is None:
        bot.send_message(
            chat_id=chat_id,
            text=reply,
            disable_web_page_preview=disable_web_page_preview,
        )
    else:
        parent_message_id = message.reply_to_message.message_id
        bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=parent_message_id,
            text=reply,
            disable_web_page_preview=disable_web_page_preview,
        )
    try:
        bot.delete_message(chat_id=chat_id, message_id=command_message_id)
    except BadRequest:
        logger.info("Command was already deleted %s", command_message_id)


def get_param(bot, update, command):
    bot_name = bot.name
    return (
        update.message.text.removeprefix(command).replace(bot_name, "").strip().lower()
    )

def format_knowledge_results(results: str) -> str:
    separator = "=" * 30
    return separator + "\n" + results + "\n" +separator


@restricted_general
def accomodation_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.accomodation())
    reply_to_message(bot, update, results)

@restricted_general
def animal_help_command(bot: Bot, update: Update):
    results = guidebook.get_animal_help()
    reply_to_message(bot, update, results)

@restricted_general
def banking_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.banking())
    reply_to_message(bot, update, results)

@restricted_general
def beauty_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.beauty())
    reply_to_message(bot, update, results)

@restricted_general
def children_lessons_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.teachers_for_peace())
    reply_to_message(bot, update, results)


@restricted_general
def cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/cities")
    results = guidebook.get_cities(name=name)
    reply_to_message(bot, update, results)


@restricted_general
def cities_all_command(bot: Bot, update: Update):
    results = guidebook.get_cities_all()
    reply_to_message(bot, update, results)


@restricted_general
def countries_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/countries")
    results = guidebook.get_countries(name=name)
    reply_to_message(bot, update, results)


@restricted_general
def dentist_command(bot: Bot, update: Update):
    results = guidebook.get_dentist()
    reply_to_message(bot, update, results)


@restricted_general
def deutsch_command(bot: Bot, update: Update):
    results = guidebook.get_german()
    reply_to_message(bot, update, results)


@restricted_general
def disabled_command(bot: Bot, update: Update):
    results = guidebook.get_disabled()
    reply_to_message(bot, update, results)

@restricted_general
def education_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.education())
    reply_to_message(bot, update, results)

@restricted_general
def evac_command(bot: Bot, update: Update):
    results = guidebook.get_evacuation()
    reply_to_message(bot, update, results)


@restricted_general
def evac_cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/evacuation_cities")
    results = guidebook.get_evacuation_cities(name=name)
    reply_to_message(bot, update, results)


@restricted_general
def freestuff_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/freestuff")
    results = guidebook.get_freestuff(name=name)
    reply_to_message(bot, update, results)

@restricted_general
def general_information_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.general_information())
    reply_to_message(bot, update, results)

@restricted_general
def germany_domestic_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/germany_domestic")
    results = guidebook.get_germany_domestic(name=name)
    reply_to_message(bot, update, results)


@restricted_general
def handbook(bot: Bot, update: Update):
    results = format_knowledge_results(commands.handbook())
    reply_to_message(bot, update, results)


@restricted_general
def help_command(bot: Bot, update: Update):
    """Send a message when the command /help is issued."""
    results = format_knowledge_results(commands.help())
    reply_to_message(bot, update, results)

@restricted_general
def homesharing_command(bot: Bot, update: Update):
    results = guidebook.get_homesharing()
    reply_to_message(bot, update, results)

@restricted_general
def hryvnia_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.hryvnia())
    reply_to_message(bot, update, results)


@restricted_general
def humanitarian_aid_command(bot: Bot, update: Update):
    results = guidebook.get_humanitarian()
    reply_to_message(bot, update, results)


@restricted_general
def jobs_command(bot: Bot, update: Update):
    results = guidebook.get_jobs()
    reply_to_message(bot, update, results)


@restricted_general
def kids_with_special_needs_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.kids_with_special_needs())
    reply_to_message(bot, update, results)


@restricted_general
def legal_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.legal())
    reply_to_message(bot, update, results)


@restricted_general
def medical_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/medical")
    results = guidebook.get_medical(name=name)
    reply_to_message(bot, update, results)


@restricted_general
def minors_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.minors())
    reply_to_message(bot, update, results)

@restricted_general
def official_information_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.official_information())
    reply_to_message(bot, update, results)


@restricted_general
def psychological_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.psychological_help())
    reply_to_message(bot, update, results)


@restricted_general
def social_adaption_command(bot: Bot, update: Update):
    # results = format_knowledge_results(commands.social_adaption())
    results = guidebook.get_social_adaptation()
    reply_to_message(bot, update, results)


@restricted_general
def social_help_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.social_help())
    reply_to_message(bot, update, results)


@restricted_general
def taxi_command(bot: Bot, update: Update):
    results = guidebook.get_taxis()
    reply_to_message(bot, update, results)


@restricted_general
def translators_command(bot: Bot, update: Update):
    results = format_knowledge_results(commands.translators())
    reply_to_message(bot, update, results)


@restricted_general
def travel_command(bot: Bot, update: Update):
    results = guidebook.get_travel()
    reply_to_message(bot, update, results)


@restricted_general
def volunteer_command(bot: Bot, update: Update):
    results = guidebook.get_volunteer()
    reply_to_message(bot, update, results)


@restricted_general
def university_command(bot: Bot, update: Update):
    results = guidebook.get_university()
    reply_to_message(bot, update, results)


def show_command_list(bot: Bot):
    command_list = [
        BotCommand("accomodation", "Search accomodation"),
        BotCommand("adaption", "Social adaption in Berlin"),
        BotCommand("banking", "Banking information"),
        BotCommand("beauty", "Beauty"),
        BotCommand(
            "cities", "Find chats for German cities, you need to pass the name of the city"
        ),
        BotCommand(
            "cities_all",
            "List all chats for German cities",
        ),
        BotCommand("children_lessons", "Online lessons for children from Ukraine"),
        BotCommand("countries", "List all chats for countries"),
        BotCommand("dentist", "Dentist help"),
        BotCommand("deutsch", "German lessons"),
        BotCommand("disabled", "Disabled people"),
        BotCommand("education", "Overview of education in Germany"),
        BotCommand("evacuation", "General evacuation info"),
        BotCommand("evacuation_cities", "Evacuation chats for ukrainian cities"),
        BotCommand("freestuff", "Free stuff in berlin"),
        BotCommand("general_information", "General information"),
        BotCommand("germany_domestic", "Germany-wide refugee centers"),
        BotCommand("handbook", "FAQ"),
        BotCommand("help", "Bot functionality"),
        BotCommand("homesharing", "Offer and find a home"),
        BotCommand("hryvnia", "Hryvnia exchange"),
        BotCommand("humanitarian", "Humanitarian aid"),
        BotCommand("jobs", "Jobs in germany"),
        BotCommand("kids_with_special_needs", "Help for children with special needs"),
        BotCommand("legal", "Chat for legal help"),
        BotCommand("medical", "Medical help"),
        BotCommand("minors", "Help for unaccompanied minors"),
        BotCommand("official_information", "Official information"),
        BotCommand("psychological", "Psychological help"),
        BotCommand("socialhelp", "Social help"),
        BotCommand("taxis", "Taxi service"),
        BotCommand("translators", "Translators"),
        BotCommand("travel", "Travel possibilities"),
        BotCommand("uni", "Universities in Germany"),
        BotCommand("vet", "Animal help"),
        BotCommand("volunteer", "Volunteer"),
    ]
    bot.set_my_commands(command_list)


def add_commands(dispatcher):
    # Commands
    dispatcher.add_handler(CommandHandler("start", start_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("stop", stop_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(CommandHandler("adminsonly", admins_only))
    dispatcher.add_handler(CommandHandler("adminsonly_revert", admins_only_revert))
    dispatcher.add_handler(CommandHandler("accomodation", accomodation_command))
    dispatcher.add_handler(CommandHandler("adaption", social_adaption_command))
    dispatcher.add_handler(CommandHandler("banking", banking_command))
    dispatcher.add_handler(CommandHandler("beauty", beauty_command))
    dispatcher.add_handler(CommandHandler("children_lessons", children_lessons_command))
    dispatcher.add_handler(CommandHandler("cities", cities_command))
    dispatcher.add_handler(CommandHandler("cities_all", cities_all_command))
    dispatcher.add_handler(CommandHandler("countries", countries_command))
    dispatcher.add_handler(CommandHandler("dentist", dentist_command))
    dispatcher.add_handler(CommandHandler("deutsch", deutsch_command))
    dispatcher.add_handler(CommandHandler("disabled", disabled_command))
    dispatcher.add_handler(CommandHandler("education", education_command))
    dispatcher.add_handler(CommandHandler("evacuation", evac_command))
    dispatcher.add_handler(CommandHandler("evacuation_cities", evac_cities_command))
    dispatcher.add_handler(CommandHandler("freestuff", freestuff_command))
    dispatcher.add_handler(CommandHandler("general_information", general_information_command))
    dispatcher.add_handler(CommandHandler("germany_domestic", germany_domestic_command))
    dispatcher.add_handler(CommandHandler("handbook", handbook))
    dispatcher.add_handler(CommandHandler("homesharing", homesharing_command))
    dispatcher.add_handler(CommandHandler("hryvnia", hryvnia_command))
    dispatcher.add_handler(CommandHandler("humanitarian", humanitarian_aid_command))
    dispatcher.add_handler(CommandHandler("jobs", jobs_command))
    dispatcher.add_handler(
        CommandHandler("kids_with_special_needs", kids_with_special_needs_command)
    )
    dispatcher.add_handler(CommandHandler("legal", legal_command))
    dispatcher.add_handler(CommandHandler("medical", medical_command))
    dispatcher.add_handler(CommandHandler("minors", minors_command))
    dispatcher.add_handler(CommandHandler("official_information", official_information_command))
    dispatcher.add_handler(CommandHandler("psychological", psychological_command))
    dispatcher.add_handler(CommandHandler("socialhelp", social_help_command))
    dispatcher.add_handler(CommandHandler("taxis", taxi_command))
    dispatcher.add_handler(CommandHandler("translators", translators_command))
    dispatcher.add_handler(CommandHandler("travel", travel_command))
    dispatcher.add_handler(CommandHandler("uni", university_command))
    dispatcher.add_handler(CommandHandler("vet", animal_help_command))
    dispatcher.add_handler(CommandHandler("volunteer", volunteer_command))


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    add_commands(dispatcher)
    show_command_list(updater.bot)

    # Messages
    dispatcher.add_handler(MessageHandler(Filters.all, delete_greetings))

    if APP_NAME == "TESTING":
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
        updater.bot.setWebhook(f"https://{APP_NAME}.herokuapp.com/{TOKEN}")

    updater.idle()


if __name__ == "__main__":
    main()
