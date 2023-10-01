FROM python:3.10-slim

WORKDIR /app

RUN apt-get update

RUN apt-get install -y ffmpeg

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .