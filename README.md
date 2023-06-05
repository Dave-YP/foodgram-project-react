# Foodgram

## Описание проекта:

Foodgram - это веб-сервис, который позволяет пользователям публиковать рецепты, подписываться на других пользователей, добавлять понравившиеся рецепты в список "Избранное" и передавать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект состоит из двух приложений: backend и frontend. Backend написан на языке Python с использованием фреймворков Django и Django REST framework, а frontend - на языке JavaScript с использованием библиотеки React.

Backend включает в себя модели данных для рецептов, пользователей и подписок, а также API для регистрации, аутентификации и управления пользователями, публикации рецептов, добавления и удаления понравившихся рецептов, получения списка продуктов для приготовления, а также схему OpenAPI с помощью фреймворка DRF Spectacular.

Frontend включает в себя компоненты для регистрации, входа, публикации рецептов, добавления и удаления понравившихся рецептов, получения списка продуктов для приготовления и отображения списка избранных рецептов.

## Технологии:

- Django - это фреймворк для создания веб-приложений на языке Python. Он предоставляет множество инструментов и библиотек для создания веб-приложений, включая маршрутизацию, шаблонизацию, аутентификацию и многое другое.

- Django REST framework - это фреймворк для создания REST API на языке Python. Он предоставляет множество инструментов и библиотек для создания REST API, включая поддержку форматов данных, аутентификацию и многое другое.

- Djoser - это фреймворк для создания REST API для регистрации, аутентификации и управления пользователями. Он предоставляет множество инструментов и библиотек для создания REST API для регистрации, аутентификации и управления пользователями, включая поддержку электронной почты и многое другое.

- DRF Spectacular - это фреймворк для создания схемы OpenAPI на основе Django REST framework. Он позволяет автоматически создавать схему OpenAPI для вашего REST API, что упрощает разработку и тестирование вашего API.

- Docker - это платформа для разработки, доставки и запуска приложений в контейнерах. Она позволяет упаковывать приложения и их зависимости в контейнеры, которые могут быть запущены на любой платформе, где установлен Docker.

- wait-for-it.sh - это скрипт на языке Bash, который ожидает и подключается к серверу перед выполнением других команд. Он может быть полезен при настройке контейнеров Docker, чтобы убедиться, что серверы, на которых они запущены, готовы к работе перед тем, как приложение начнет работать.

## Запуск проекта через Docker(localhost):

Для запуска проекта необходимо выполнить следующие шаги:

 - [ ] Клонировать репозиторий:
```
git clone https://github.com/Dave-YP/foodgram-project-react
```

 - [ ] Переименовать файл example.env в .env и заполнить его своими
       данными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=poostgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost/db
DB_PORT=5432
SECRET_KEY='secretgenerate'
DEBUG = True
```

> Генератор секретного ключа: infra/secretgenerate.py

 - [ ] Запустить Docker:
```
 docker-compose up -d
```

 - [ ] Зарегистрировать суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```

 - [ ] Запустить проект:

 
http://localhost/

 - [ ] После запуска проекта будут доступны следующие ссылки(API):

> Swagger UI:

http://localhost/api/schema/swagger-ui/

> ReDoc от DRF Spectacular:

http://localhost/api/schema/redoc/

> ReDoc проекта:

http://localhost/api/docs/redoc.html

> Скачать схему проекта можно по ссылке:

http://localhost/api/schema/


### **Дополнительная информация:**

 - При сборке контейнеров в файле entrypoint.sh прописаны команды, которые можно отредактировать:

команды в entrypoint.sh:

> Выполняем миграции и загружаем данные:
> 
> python manage.py makemigrations recipes
> 
> python manage.py makemigrations users
> 
> python manage.py migrate
> 
> python manage.py collectstatic --no-input
> 
> python manage.py load_ingredients
> 
> python manage.py load_tags

 - Список полезных команд:
 
```
docker compose exec backend python manage.py makemigrations recipes
docker compose exec backend python manage.py makemigrations users
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py load_ingredients
docker compose exec backend python manage.py load_tags
```

 - requirements.txt:
 
    Django==4.2.1
    django-cors-headers==3.11.0
    django-colorful==1.3
    django-filter==22.1
    djangorestframework==3.14.0
    djoser==2.1.0
    drf-extra-fields==3.5.0
    drf-spectacular==0.25.0
    flake8==6.0.0
    gunicorn==20.1.0
    importlib-metadata==4.12.0
    Markdown==3.4.1
    psycopg2-binary==2.9.3
    python-dotenv==0.21.0
    reportlab==3.6.1
    zipp==3.15.0
