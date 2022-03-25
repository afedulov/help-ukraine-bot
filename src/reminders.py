from telegram import Bot, Message, Update, InputMedia, InputMediaPhoto, ParseMode
from telegram.ext import Job, JobQueue
from typing import Tuple
import logging
import os

from src import commands

logger = logging.getLogger(__name__)

REMINDER_MESSAGE = "I WILL POST PINNED MESSAGE HERE"
REMINDER_PINNED_INTERVAL = 30 * 60
REMINDER_SOCIAL_INTERVAL = 10 * 60
REMINDER_SAFE_ON_THE_ROAD_INTERVAL = 1 * 60
PINNED_JOB = "pinned"
SOCIAL_JOB = "social"
SAFE_ON_THE_ROAD_JOB = "safe_on_the_road"
JOBS_NAME = [PINNED_JOB, SOCIAL_JOB, SAFE_ON_THE_ROAD_JOB]


def send_social_reminder(bot: Bot, job: Job):
    """send_reminder"""
    chat_id = job.context
    logger.info("Sending a social reminder to chat %s", chat_id)
    results = commands.social_help()
    bot.send_message(chat_id=chat_id, text=results, disable_web_page_preview=True)


def send_pinned_reminder(bot: Bot, job: Job):
    """send_reminder"""
    chat_id = job.context
    chat = bot.get_chat(chat_id)
    msg: Message = chat.pinned_message
    logger.info("Sending pinned message to chat %s", chat_id)

    if msg:
        bot.forward_message(chat_id, chat_id, msg.message_id)
    else:
        bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)


def send_safe_on_the_road_reminder(bot: Bot, job: Job):
    chat_id = job.context
    logger.info("Sending a safe on the road reminder to chat %s", chat_id)
    # photo_url = 'https://www.kok-gegen-menschenhandel.de/fileadmin/user_upload/medien/Flucht_und_Menschenhandel/Ukraine_Flyer_UA_Long_Version.png'
    # bot.sendPhoto(msg['chat']['id'], (os.path.basename(filepath), open(filepath)))
    # path = os.path.basename('src/resources/safe-on-the-road/ua.png')
    bot.send_photo(chat_id, (open('src/resources/safe-on-the-road/ua.png')))


def add_job(bot: Bot, update: Update, job_queue: JobQueue, intervals, job_name, reminder):
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=f"I'm starting {job_name} every {intervals}s.",
    )
    job_queue.run_repeating(
        reminder,
        intervals,
        first=1,
        context=chat_id,
        name=job_name,
    )


def reminder(bot: Bot, update: Update, job_queue: JobQueue):
    chat_id = update.message.chat_id
    logger.info("Started reminders in channel %s", chat_id)

    jobs: Tuple[Job] = tuple()
    job_queue.jobs()

    #  Restart already existing jobs
    for job in jobs:
        if not job.enabled:
            job.enabled = True

    # Start a new job if there was none previously
    if not jobs:
        # add_job(bot, update, job_queue, REMINDER_PINNED_INTERVAL, PINNED_JOB, send_pinned_reminder)
        # add_job(bot, update, job_queue, REMINDER_SOCIAL_INTERVAL, SOCIAL_JOB, send_social_reminder)
        add_job(bot, update, job_queue, REMINDER_SAFE_ON_THE_ROAD_INTERVAL, SAFE_ON_THE_ROAD_JOB,
                send_safe_on_the_road_reminder)
