# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ffmpeg curl unzip \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY requirements-youtube.txt requirements-youtube.txt
RUN pip install --no-cache-dir -r requirements-youtube.txt

COPY . .

RUN sed -i 's/\r$//' start.sh

ENV PYTHONUNBUFFERED=1

CMD ["bash", "./start.sh"]
