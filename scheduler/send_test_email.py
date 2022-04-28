import sys
import os
import django
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--project_path", required=False, type=str)
parser.add_argument("--recipients", type=str)
args = parser.parse_args()

if args.project_path:
    sys.path.append(args.project_path)
else:
    sys.path.append('../')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shareboat.settings')
django.setup()

from emails.utils import send_email
recipients = args.recipients.split(';')
send_email("Тестовое письмо", "Тестовое письмо", recipients)