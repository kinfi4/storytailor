FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    ratbagd \
    piper \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m piper.download_voices en_US-lessac-medium

COPY app/ ./app/

EXPOSE 8000

CMD ["python", "-m", "app"]
