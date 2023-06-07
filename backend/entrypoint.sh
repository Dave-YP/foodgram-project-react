#!/bin/bash

# Ожидаем доступности базы данных
./wait-for-it.sh db:5432 --timeout=30

# Выполняем миграции и загружаем данные
python manage.py makemigrations recipes
python manage.py makemigrations users
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py load_ingredients
python manage.py load_tags

# Запускаем сервер
exec gunicorn foodgram.wsgi:application --bind 0:8000
