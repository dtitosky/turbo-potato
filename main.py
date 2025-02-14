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
from chatgpt_client import get_analysis_from_chatgpt

# Логирование
logging.basicConfig(
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для распознавания анализов крови. Пришлите мне PDF или фото анализа, и я всё обработаю."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пришлите файл PDF или изображение с анализом крови. Я распознаю его, "
        "сохраню в базу и дам краткие рекомендации."
    )

async def chunked_send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """
    Делим длинный текст на несколько сообщений (не более 4096 символов каждое).
    """
    chunk_size = 4096
    for i in range(0, len(text), chunk_size):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text[i : i + chunk_size]
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Скачиваем документ (PDF или изображение)
    document = update.message.document
    file_id = document.file_id
    file_obj = await context.bot.get_file(file_id)
    file_bytes = await file_obj.download_as_bytearray()

    test_text = ""

    # Проверяем расширение
    file_name = document.file_name
    if file_name.lower().endswith(".pdf"):
        # Парсим PDF
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                test_text += text + "\n"
    else:
        # Предполагаем изображение
        image = Image.open(BytesIO(file_bytes))
        test_text = pytesseract.image_to_string(image, lang='rus+eng')  # lang можно настроить

    # Сохраняем в БД
    user_id = update.effective_user.id
    save_blood_test(user_id, test_text)

    # Выполняем системный анализ (локальный, как раньше)
    analysis_result = analyze_blood_data(test_text)
    # Получаем анализ от ChatGPT
    chatgpt_analysis = get_analysis_from_chatgpt(test_text)

    result_msg = (
        f"Распознанный текст:\n{test_text}\n\n"
        f"Системный анализ:\n{analysis_result}\n\n"
        f"Анализ от ChatGPT:\n{chatgpt_analysis}"
    )
    await chunked_send_text(update, context, result_msg)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь присылает фото напрямую (без документа), обрабатываем аналогично
    photo = update.message.photo[-1]  # Берём самое большое фото
    file_obj = await context.bot.get_file(photo.file_id)
    file_bytes = await file_obj.download_as_bytearray()

    image = Image.open(BytesIO(file_bytes))
    test_text = pytesseract.image_to_string(image, lang='rus+eng')

    # Сохраняем в БД
    user_id = update.effective_user.id
    save_blood_test(user_id, test_text)

    # Анализ
    analysis_result = analyze_blood_data(test_text)
    from chatgpt_client import get_analysis_from_chatgpt
    chatgpt_analysis = get_analysis_from_chatgpt(test_text)

    result_msg = (
        f"Распознанный текст:\n{test_text}\n\n"
        f"Системный анализ:\n{analysis_result}\n\n"
        f"Анализ от ChatGPT:\n{chatgpt_analysis}"
    )
    await chunked_send_text(update, context, result_msg)

async def get_tests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Возвращает все анализы пользователя
    user_id = update.effective_user.id
    tests = get_user_tests(user_id)

    if not tests:
        await update.message.reply_text("У вас нет сохранённых анализов.")
        return

    msg = "Ваши анализы:\n"
    for t in tests:
        msg += f"ID {t['id']} - {t['timestamp']}:\n{t['test_text'][:100]}...\n\n"
    await update.message.reply_text(msg)

def main():
    # Создаём таблицы (на всякий случай)
    create_tables()

    # Инициализируем приложение
    app = ApplicationBuilder().token(API_TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("get_tests", get_tests_command))

    # Обработка документов (PDF, doc и т.д.)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    # Обработка фото
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main() 