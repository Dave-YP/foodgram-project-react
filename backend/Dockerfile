FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

COPY wait-for-it.sh /app/wait-for-it.sh
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/wait-for-it.sh /app/entrypoint.sh

COPY . .
CMD ["/app/entrypoint.sh"]
