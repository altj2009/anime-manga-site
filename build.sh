#!/usr/bin/env bash
# Выход при ошибке
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Сбор статических файлов (CSS, JS, картинки)
python manage.py collectstatic --no-input

# Применение миграций базы данных
python manage.py migrate