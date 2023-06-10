FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

COPY wait-for-it.sh /app/wait-for-it.sh
RUN apt-get update && apt-get install -y dos2unix
RUN dos2unix /app/wait-for-it.sh && chmod +x /app/wait-for-it.sh

COPY . .

CMD /bin/bash -c "./wait-for-it.sh db:5432 --timeout=30 && \
                 python manage.py makemigrations recipes && \
                 python manage.py makemigrations users && \
                 python manage.py migrate && \
                 python manage.py collectstatic --no-input && \
                 python manage.py load_ingredients && \
                 python manage.py load_tags && \
                 exec gunicorn foodgram.wsgi:application --bind 0:8000"
