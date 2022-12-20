# Shareboat

Сайт для аренды лодок

## Первый запуск

1. Создать файл `.env` по аналогии с файлом `.env.example`
2. Создать файл `app/.env` по аналогии с файлом `app/.env.example`

## Запуск в Docker

1. Запустить докер `docker compose up -d --build`

## Локальный запуск для разработки и тестирования

1. Запустить PostgreSQL
2. Перейти в папку с приложением `cd app`
3. Создать виртуальное Python-окружение `python -m venv venv`
4. Установить зависимости `pip install -r requirements.txt`
5. Запустить приложение `python manage.py runserver`
 
## Линтер

1. Перейти в папку с приложением `cd app`
2. Запуск `flake8`. Конфигурация находится в `setup.cfg`

## Тестирование

1. Запустить PostgreSQL
2. Перейти в папку с приложением `cd app`
3. Запустить тест `coverage run manage.py test -v 2`
4. Сформировать отчет `coverage html`