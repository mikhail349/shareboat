from .models import TelegramUser


def verify_tg_code(chat_id, code):
    try:
        tguser = TelegramUser.objects.get(
            verification_code=code, chat_id__isnull=True)
        tguser.chat_id = chat_id
        tguser.save()
        return True
    except TelegramUser.DoesNotExist:
        return False
