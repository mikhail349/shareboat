import sys
import os

import django
import argparse

from emails.utils import send_email


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Отправляет тестовое письмо")
    parser.add_argument("--project_path", required=False, type=str,
                        help="Путь проекта. По умолчанию ../", default='../')
    parser.add_argument("--recipients", type=str,
                        help="Список получателей через ;")
    args = parser.parse_args()

    sys.path.append(args.project_path)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shareboat.settings')
    django.setup()

    recipients = args.recipients.split(';')
    send_email("Тестовое письмо", "Тестовое письмо", recipients)
