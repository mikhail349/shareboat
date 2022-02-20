from telegram import ParseMode, BotCommand
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
from .decorators import login_required

from booking.models import Booking
from boat.models import Boat
from user.models import TelegramUser
from user.utils import verify_tg_code  

AUTH = 0

anon_commands = [
    BotCommand('start', 'начать общение'),
    BotCommand('cancel', 'завершить диалог'),
    BotCommand('auth', 'авторизоваться'),
]

auth_commands = [
    BotCommand('myboats', 'мои лодки'),
    BotCommand('mybookings', 'мои бронирования'),
]

def start(update, context):
    #update.message.reply_text("Вас приветствует <b>Sharebot</b>!", parse_mode=ParseMode.HTML)
    msg = "Вас приветствует <b>Shareboat</b>!\n\n"
    user = TelegramUser.get_user(update)
    if user:
        msg += "Вам доступны команды:\n"
        for auth_command in auth_commands:
            msg += f'\n/{auth_command.command} - {auth_command.description}'
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        return 

    update.message.reply_text(msg + "Похоже, вы еще не авторизованы.\nЧтобы сделать это, выполните команду /auth", parse_mode=ParseMode.HTML)

def auth(update, context):
    chat_id = update.message.from_user.id
    if TelegramUser.objects.filter(chat_id=chat_id).exists():
        update.message.reply_text("Вы уже авторизованы.")
        return

    update.message.reply_text(
        """Пожалуйста, введите шестизначный код авторизации.\n""" +
        """Чтобы его получить перейдите на <a href="https://sbtest.posse.ru/user/update/">страницу своего профиля</a>.\n\n""" + 
        """Вы всегда можете прекратить этот диалог командой /cancel""", 
    parse_mode=ParseMode.HTML)
    return AUTH

def verify_code(update, context):
    
    user_id = update.message.from_user.id
    code = update.message.text
    res = verify_tg_code(user_id, code)
    
    if res:
        msg = "Отлично! Теперь Вам доступны следующие команды:\n"
        for auth_command in auth_commands:
            msg += f'\n/{auth_command.command} - {auth_command.description}'

        update.message.reply_text(msg)
        return ConversationHandler.END

    update.message.reply_text('Неверный код.') 

def wrong_code(update, context):
    update.message.reply_text('Это не похоже на шестизначный код.') 

def cancel(update, context):
    update.message.reply_text("До встречи!")
    return ConversationHandler.END

def error(update, context):
    update.message.reply_text("Я Вас не понимаю.\n\nЧтобы начать общение, выполните команду /start") 

def no_conv(update, context):
    update.message.reply_text("Нет активных диалогов.\n\nЧтобы начать общение, выполните команду /start")    

@login_required()
def myboats(update, context, user):
    cnt = Boat.objects.filter(owner=user).count()
    update.message.reply_text('У Вас лодок: %s' % cnt)

@login_required()
def mybookings(update, context, user):
    cnt = Booking.objects.filter(renter=user).count()
    update.message.reply_text('У Вас бронирований: %s' % cnt)    

def setup_handlers(dispatcher):

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('auth', auth)
        ],
        states={
            AUTH: [
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.regex('^\d{6}$'), verify_code),
                MessageHandler(Filters.text, wrong_code)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel)
        ],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('myboats', myboats))
    dispatcher.add_handler(CommandHandler('mybookings', mybookings))
    dispatcher.add_handler(CommandHandler('cancel', no_conv))
    dispatcher.add_handler(MessageHandler(Filters.text, error))

def setup_commands(bot):
    bot.set_my_commands(anon_commands + auth_commands)