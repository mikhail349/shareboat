#!/bin/bash
[[ -z "$DATABASE_HOST" ]] && { echo "Parameter DATABASE_HOST is empty" ; exit 1; }
[[ -z "$DATABASE_PORT" ]] && { echo "Parameter DATABASE_PORT is empty" ; exit 1; }

while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
    sleep 0.1
done

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000