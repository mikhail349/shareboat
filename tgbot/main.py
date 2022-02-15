import os
import django
import sys
import logging

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

module = os.path.split(os.path.dirname(__file__))[0]
sys.path.append(module)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shareboat.settings")
django.setup()

logger = logging.getLogger('tgbot')

updater = Updater(token='2109074698:AAGejKYA-fzzLtJbB4ETitg0_kiRXN3lsP8', use_context=True)
dispatcher = updater.dispatcher

def get_user_display_name(user):
    return user['first_name'] or user['username']
#user['first_name'], user['last_name'], user['username']

def start(bot, update):
    display_name = get_user_display_name(bot.message.from_user)
    logger.info("Вызвали start")
    bot.message.reply_text("Привет, %s. Вас приветствует бот-Sharebot" % display_name, reply_markup=main_menu_keyboard())

def get_boats_count(bot, update):
    from boat.models import Boat
    cnt = Boat.objects.all().count()
    bot.callback_query.message.edit_text('Лодок в БД: %s' % cnt)
    #bot.message.reply_text("Вас приветствует бот-Sharebot", reply_markup=main_menu_keyboard())

def echo(update, context):
    display_name = get_user_display_name(update.message.from_user)
    logger.info("%s написал сообщение: %s" % (display_name, update.message.text))
    #context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Получить кол-во лодок в БД', callback_data='get_boats_count')],]
  return InlineKeyboardMarkup(keyboard)

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(get_boats_count, pattern='get_boats_count'))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

updater.start_polling(poll_interval=0.1)
updater.idle()


'''
bot = telebot.TeleBot('2109074698:AAGejKYA-fzzLtJbB4ETitg0_kiRXN3lsP8')

@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Я на связи. Напиши мне что-нибудь )')

bot.polling(none_stop=True, interval=0)
'''
