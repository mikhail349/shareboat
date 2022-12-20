from telegram import ParseMode

from .views import bot


def send_message(user, html):
    if hasattr(user, 'telegramuser'):
        chat_id = user.telegramuser.chat_id
        bot.send_message(chat_id, html, parse_mode=ParseMode.HTML)
