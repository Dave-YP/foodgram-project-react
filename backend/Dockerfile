FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

COPY --chmod=755 wait-for-it.sh /app/wait-for-it.sh
RUN apt-get update && apt-get install -y dos2unix
COPY --chmod=755 entrypoint.sh /app/entrypoint.sh

COPY . .
CMD ["/app/entrypoint.sh"]
