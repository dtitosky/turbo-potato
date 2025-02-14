# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем Tesseract (если используется OCR)
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . /app

# Запускаем приложение (используем webhook-режим, поэтому работают HTTP запросы)
CMD ["python", "main.py"] 