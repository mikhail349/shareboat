from user.models import TelegramUser

def login_required():
    def actual_decorator(f):
        def wrapper(update, context, *args, **kwargs):         
            user = TelegramUser.get_user(update)
            if user:
                return f(update, context, user=user, *args, **kwargs)
            update.message.reply_text("Похоже, вы еще не авторизованы.\n\nЧтобы сделать это, выполните команду /auth")
        return wrapper
    return actual_decorator