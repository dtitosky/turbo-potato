# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем Tesseract (если нужно)
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . /app

# Запускаем приложение
CMD ["python", "main.py"] 