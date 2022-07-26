from .views import bot
from telegram import ParseMode

def send_message(user, html):
    if hasattr(user, 'telegramuser'):
        chat_id = user.telegramuser.chat_id
        bot.send_message(chat_id, html, parse_mode=ParseMode.HTML)