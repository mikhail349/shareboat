# Shareboat

Сайт для аренды лодок. Позволяет сдавать лодку и брать в аренду. 

## Первый запуск

1. Создать файл `.env` по аналогии с файлом `.env.example`
2. Создать файл `app/.env` по аналогии с файлом `app/.env.example`

## Переменные среды для запуска в режиме разработки
Чтобы не настраивать RECAPTCHA, Telegram-bot и email рассылку, можно перевести `DEBUG=True`, а значения переменных оставить пустыми:
```
DEBUG=True

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_SSL=
DEFAULT_FROM_EMAIL=
SERVER_EMAIL=

RECAPTCHA_CLIENTSIDE_KEY=
RECAPTCHA_SERVERSIDE_KEY=

TGBOT_TOKEN=

SUPPORT_PHONE=
SUPPORT_EMAIL=
SUPPORT_VK=
SUPPORT_TELEGRAM=
```

## Запуск в Docker

1. Запустить докер `docker compose up -d --build`

## Админ-панель
Находится по URL `/admin/`

## Локальный запуск для разработки и тестирования

1. Запустить PostgreSQL `docker compose -f docker-compose.dev.yml -f docker-compose.yml up db -d`
2. Перейти в папку с приложением `cd app`
3. Создать виртуальное Python-окружение `python -m venv venv`
4. Установить зависимости `pip install -r requirements.txt`
6. Накатить миграции `python manage.py migrate`
7. Создать суперпользователя `python manage.py createsuperuser --noinput`
8. Запустить приложение `python manage.py runserver`
 
## Линтер

1. Запуск `flake8 app --config=app/setup.cfg`

## Локальное тестирование

1. Сменить название БД на тестовую в файлах `.env` и `app/.env` 
2. Запустить PostgreSQL `docker compose -f docker-compose.dev.yml -f docker-compose.yml up db -d`
3. Перейти в папку с приложением `cd app`
4. Создать виртуальное Python-окружение `python -m venv venv`
5. Установить зависимости `pip install -r requirements.txt`
6. Собрать статику `python manage.py collectstatic --noinput`
7. Запустить тест `coverage run manage.py test -v 2`. Либо с параметром `--exclude-tag=slow`, чтобы не тестировать скорость
8. Сформировать отчет `coverage html`