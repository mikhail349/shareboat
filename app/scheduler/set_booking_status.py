import argparse
import os
import sys

import django

from booking.utils import autoupdate_statuses

desc = """Обновляет статусы бронирований:
1. Проставляет "Отменена" для броней,
    у которых статус "Требуется предоплата" и срок предоплаты истек.
2. Проставляет "Активна" для броней,
    у которых статус "Подтверждена" и срок аренды начался.
2. Проставляет "Завершена" для броней,
    у которых статус "Активна" и срок аренды закончился.
"""

parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--project_path", required=False, type=str,
                    help="Путь проекта. По умолчанию ../", default='../')
args = parser.parse_args()

sys.path.append(args.project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shareboat.settings')
django.setup()

autoupdate_statuses()
