import sys
import os
import django
import argparse

desc = """Обновляет статусы бронирований:
1. Проставляет "Отменена" для броней, у которых статус "Требуется предоплата" и срок предоплаты истек.
2. Проставляет "Активна" для броней, у которых статус "Подтверждена" и срок аренды начался.
2. Проставляет "Завершена" для броней, у которых статус "Активна" и срок аренды закончился.
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--project_path", required=False, type=str, help="Путь проекта. По умолчанию ../", default='../')
args = parser.parse_args()

sys.path.append(args.project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shareboat.settings')
django.setup()

from django.utils import timezone
from booking.models import Booking

# decline if prepayment date is out
Booking.objects.filter(status=Booking.Status.PREPAYMENT_REQUIRED, prepayment__until__lte=timezone.now()).update(status=Booking.Status.DECLINED)

# active if period started
Booking.objects.filter(status=Booking.Status.ACCEPTED, start_date__lte=timezone.now()).update(status=Booking.Status.ACTIVE)

# done if period finished
Booking.objects.filter(status=Booking.Status.ACTIVE, end_date__lte=timezone.now()).update(status=Booking.Status.DONE)