# Shareboat

Сайт для аренды лодок

## Первый запуск

1. Создать файл `.env` по аналогии с файлом `.env.example`.
2. Создать файл `app/.env` по аналогии с файлом `app/.env.example`.

### Запуск в Docker

1. Запустить докер `docker-compose up --build`

### Локальный запуск

1. Запустить БД с открытым портом `docker-compose -f docker-compose.yml -f docker-compose.dev.yaml up db -d`
1. Перейти в папку с приложением `cd app`
2. Создать виртуальное Python-окружение `python -m venv venv`
3. Установить зависимости `pip install -r requirements.txt`
3. Запустить приложение `python manage.py runserver`
 
## Линтер

1. Перейти в папку с приложением `cd app`
2. Запуск `flake8`. Конфигурация находится в `setup.cfg`

## Тестирование

1. Запустить БД с открытым портом `docker-compose -f docker-compose.yml -f docker-compose.dev.yaml up db -d`
2. Перейти в папку с приложением `cd app`
3. Запустить тест `coverage run manage.py test -v 2`
4. Сформировать отчет `coverage html`