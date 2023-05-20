FROM python:3.11.3
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt upgrade -y
RUN apt install -y ffmpeg
COPY . /app/
