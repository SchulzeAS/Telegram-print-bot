#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import requests
import wget
import logging
import json
from telegram import __version__ as TG_VER
import os

BOT_TOKEN = "YOUR_TOKEN"
PRINTER_NAME = 'YOUR_PRINTER'

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}, ich bin Günther und ich helfe dir beim drucken! Schicke mir einfach die Dateien und ich drucke sie für dich aus!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def print_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Ich würde echt gerne drucken, nur leider bin ich zu dumm :c!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text("Du hast mir ein Foto geschickt!")
    file_id = update.message.photo[2].file_id
    file_path_request_url ="https://api.telegram.org/bot{TOKEN}/getFile?file_id={FID}"
    path_r  = requests.get(file_path_request_url.format(TOKEN = BOT_TOKEN,FID = file_id))
    #file_path_requested = (path_r.json().result.file_path)
    data = path_r.json()
    file_path_requested = data['result']['file_path']
    file_id_request_url = "https://api.telegram.org/file/bot{TOKEN}/{PATH}"
    filename = wget.download(file_id_request_url.format(TOKEN = BOT_TOKEN, PATH = file_path_requested ))
    os.system("lpr -P {PRINTER} -o media=a4 {FILENAME}".format(PRINTER = PRINTER_NAME, FILENAME = filename))

async def file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Du hast mir eine Datei geschickt!")
    file_id =update.message.document.file_id
    file_path_request_url ="https://api.telegram.org/bot{TOKEN}/getFile?file_id={FID}"
    path_r  = requests.get(file_path_request_url.format(TOKEN = BOT_TOKEN,FID = file_id))
    #file_path_requested = (path_r.json().result.file_path)
    data = path_r.json()
    file_path_requested = data['result']['file_path']
    file_id_request_url = "https://api.telegram.org/file/bot{TOKEN}/{PATH}"
    filename = wget.download(file_id_request_url.format(TOKEN = BOT_TOKEN, PATH = file_path_requested ))
    os.system("lpr -P {PRINTER} -o media=a4 {FILENAME}".format(PRINTER = PRINTER_NAME, FILENAME = filename))


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("drucken", print_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.PHOTO,photo))
    application.add_handler(MessageHandler(filters.Document.ALL,file))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
if __name__ == "__main__":
    main()
