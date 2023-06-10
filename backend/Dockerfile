FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

COPY wait-for-it.sh /app/wait-for-it.sh
RUN apt-get update && apt-get install -y dos2unix
COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/wait-for-it.sh && dos2unix /app/entrypoint.sh && chmod +x /app/wait-for-it.sh /app/entrypoint.sh

COPY . .
CMD ["/app/entrypoint.sh"]