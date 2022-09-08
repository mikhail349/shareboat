# Shareboat

Сайт для аренды лодок

## Первый запуск

1. Создать виртуальное Python-окружение `python -m venv venv`
2. Установить зависимости `pip install -r requirements.txt`
3. Установить pre-commit hook `pre-commit install`
 
## Линтер

Запуск `flake8`. Конфигурация находится в `setup.cfg`

## Тестирование

1. Запустить тест `coverage run manage.py test -v 2`
2. Сформировать отчет `coverage html`