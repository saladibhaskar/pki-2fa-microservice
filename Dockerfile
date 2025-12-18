FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod 0644 cron/2fa-cron && crontab cron/2fa-cron
RUN mkdir -p /data /cron

EXPOSE 8080

CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
