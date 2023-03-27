import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.bot import Bot
from telegram.ext import Dispatcher

from .handlers import setup_commands, setup_handlers


@csrf_exempt
def webhook(request):
    update = Update.de_json(json.loads(request.body), bot)
    dispatcher.process_update(update)
    return JsonResponse({"ok": "Request processed"})


if settings.TGBOT_TOKEN:
    bot = Bot(settings.TGBOT_TOKEN)
    dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
    setup_commands(bot)
    setup_handlers(dispatcher)
