import argparse
import os
import sys

import django

from booking.utils import autoremind_prepayment

desc = """Рассылает напоминания:
1. Арендаторам, что необходимо внести предоплату.
2. Арендодателям, что необходимо сменить статус, если предоплата внесена.
"""

parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--project_path", required=False, type=str,
                    help="Путь проекта. По умолчанию ../", default='../')
args = parser.parse_args()

sys.path.append(args.project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shareboat.settings')
django.setup()

autoremind_prepayment()
