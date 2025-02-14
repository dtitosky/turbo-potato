import logging
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import pdfplumber
import pytesseract
from PIL import Image
from io import BytesIO

from config import API_TOKEN
from analysis import analyze_blood_data
from database import create_tables, save_blood_test, get_user_tests
from chatgpt_client import get_analysis_from_chatgpt, get_recommendations_from_chatgpt

# Логирование
logging.basicConfig(
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для распознавания анализов крови. Пришлите мне PDF или фото анализа, и я обработаю их."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пришлите документ (PDF) или фото анализа крови. Я распознаю текст, сохраню данные и передам их для анализа."
    )

async def get_tests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tests = get_user_tests(user_id)
    if not tests:
        await update.message.reply_text("У вас нет сохранённых анализов.")
        return
    msg = "Ваши анализы:\n"
    for t in tests:
        msg += f"ID {t['id']} - {t['timestamp']}:\n{t['test_text'][:100]}...\n\n"
    await update.message.reply_text(msg)

async def chunked_send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """
    Делит длинный текст на куски (не более 4096 символов) и отправляет их.
    """
    chunk_size = 4096
    for i in range(0, len(text), chunk_size):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text[i : i + chunk_size]
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Пример кода для скачивания PDF-документа и распознавания текста:
    document = update.message.document
    file_obj = await context.bot.get_file(document.file_id)
    file_bytes = await file_obj.download_as_bytearray()

    test_text = ""
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                test_text += text + "\n"
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке PDF: {e}")
        return

    # Отладочный вывод распознанного текста
    print("Распознанный текст (debug):", repr(test_text))

    if not test_text.strip():
        await update.message.reply_text("Кажется, я не смог распознать текст анализа. Пожалуйста, загрузите более чёткий файл.")
        return

    # Сохраняем полученные данные (при необходимости)
    user_id = update.effective_user.id
    save_blood_test(user_id, test_text)

    # Получаем анализ (резюме) от ChatGPT на основе распознанного текста
    analysis_result = get_analysis_from_chatgpt(test_text)

    # Далее передаём анализ в ChatGPT для получения подробных рекомендаций
    recommendations = get_recommendations_from_chatgpt(analysis_result)

    result_msg = (
        f"Анализ:\n{analysis_result}\n\n"
        f"Рекомендации:\n{recommendations}"
    )
    await chunked_send_text(update, context, result_msg)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Пример кода для скачивания фото и распознавания текста via OCR:
    photo = update.message.photo[-1]  # выбираем самое большое изображение
    file_obj = await context.bot.get_file(photo.file_id)
    file_bytes = await file_obj.download_as_bytearray()
    try:
        image = Image.open(BytesIO(file_bytes))
        test_text = pytesseract.image_to_string(image, lang='rus+eng')
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке изображения: {e}")
        return

    print("Распознанный текст (debug):", repr(test_text))

    if not test_text.strip():
        await update.message.reply_text("Кажется, я не смог распознать текст анализа. Пожалуйста, загрузите более чёткое изображение.")
        return

    # Сохраняем данные (при необходимости)
    user_id = update.effective_user.id
    save_blood_test(user_id, test_text)

    # Получаем анализ (резюме) от ChatGPT на основе распознанного текста
    analysis_result = get_analysis_from_chatgpt(test_text)

    # Передаём анализ в ChatGPT для получения подробных рекомендаций
    recommendations = get_recommendations_from_chatgpt(analysis_result)

    result_msg = (
        f"Анализ:\n{analysis_result}\n\n"
        f"Рекомендации:\n{recommendations}"
    )
    await chunked_send_text(update, context, result_msg)

def main():
    # Создаём или обновляем таблицы
    create_tables()

    app = ApplicationBuilder().token(API_TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("get_tests", get_tests_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Используем webhook-режим для работы на Railway
    port = int(os.environ.get("PORT", 8080))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL не установлен в переменных окружения")
    webhook_url = f"{WEBHOOK_URL}/{API_TOKEN}"

    app.run_webhook(
         listen="0.0.0.0",
         port=port,
         url_path=API_TOKEN,
         webhook_url=webhook_url
    )

if __name__ == "__main__":
    main() 