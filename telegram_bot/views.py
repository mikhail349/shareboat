from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from telegram import Update
from telegram.bot import Bot
from telegram.ext import Dispatcher
from django.conf import settings

import json

from .handlers import setup_handlers, setup_commands


@csrf_exempt
def webhook(request):
    update = Update.de_json(json.loads(request.body), bot)
    dispatcher.process_update(update)
    return JsonResponse({"ok": "Request processed"})


bot = Bot(settings.TGBOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
setup_commands(bot)
setup_handlers(dispatcher)
