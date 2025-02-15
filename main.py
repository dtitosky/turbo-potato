import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

import pdfplumber
import pytesseract
from PIL import Image
from io import BytesIO

from config import API_TOKEN
from analysis import analyze_blood_data
from database import create_tables, save_blood_test, get_user_tests
from chatgpt_client import get_analysis_from_chatgpt_vision

# Логирование
logging.basicConfig(
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)

# Добавим константу для callback_data
GET_RECOMMENDATIONS = "get_nutrition_recommendations"

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
    # Получаем документ для прямой отправки в ChatGPT Vision
    document = update.message.document
    file_obj = await context.bot.get_file(document.file_id)
    file_bytes = await file_obj.download_as_bytearray()
    file_name = document.file_name
    print(f"Получен документ: {file_name}, размер: {len(file_bytes)} байт")
    
    await update.message.reply_text("🔍 Идет проверка и распознавание документа...")
    
    # Получаем анализ с использованием ChatGPT Vision
    vision_analysis = get_analysis_from_chatgpt_vision(file_bytes, file_name)
    
    # Если получили сообщение об ошибке (не анализ крови), просто возвращаем его
    if "К сожалению, загруженный файл не является анализом крови" in vision_analysis:
        await chunked_send_text(update, context, vision_analysis)
        return
    
    # Если это анализ крови, отправляем промежуточное сообщение
    await update.message.reply_text("✅ Анализ крови успешно распознан. Пожалуйста, подождите, идет подробный анализ данных...")
    
    # Сохраняем анализ в контексте для последующего использования
    context.user_data['last_analysis'] = vision_analysis
    
    result_msg = vision_analysis
    await chunked_send_text(update, context, result_msg)
    
    # Добавляем кнопку для запроса рекомендаций
    keyboard = [[InlineKeyboardButton("Да, хочу получить рекомендации по питанию", callback_data=GET_RECOMMENDATIONS)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Хотите получить рекомендации по питанию на основе ваших анализов?",
        reply_markup=reply_markup
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем фото для прямой отправки в ChatGPT Vision
    photo = update.message.photo[-1]
    file_obj = await context.bot.get_file(photo.file_id)
    file_bytes = await file_obj.download_as_bytearray()
    file_name = "photo.jpg"  # Можно задать имя по умолчанию
    print(f"Получено фото, размер: {len(file_bytes)} байт")
    
    await update.message.reply_text("🔍 Идет проверка и распознавание изображения...")
    
    # Получаем анализ с использованием ChatGPT Vision
    vision_analysis = get_analysis_from_chatgpt_vision(file_bytes, file_name)
    
    # Если получили сообщение об ошибке (не анализ крови), просто возвращаем его
    if "К сожалению, загруженный файл не является анализом крови" in vision_analysis:
        await chunked_send_text(update, context, vision_analysis)
        return
    
    # Если это анализ крови, отправляем промежуточное сообщение
    await update.message.reply_text("✅ Анализ крови успешно распознан. Пожалуйста, подождите, идет подробный анализ данных...")
    
    # Сохраняем анализ в контексте для последующего использования
    context.user_data['last_analysis'] = vision_analysis
    
    result_msg = vision_analysis
    await chunked_send_text(update, context, result_msg)
    
    # Добавляем кнопку для запроса рекомендаций
    keyboard = [[InlineKeyboardButton("Да, хочу получить рекомендации по питанию", callback_data=GET_RECOMMENDATIONS)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Хотите получить рекомендации по питанию на основе ваших анализов?",
        reply_markup=reply_markup
    )

async def handle_recommendation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия кнопки запроса рекомендаций"""
    query = update.callback_query
    await query.answer()
    
    if query.data == GET_RECOMMENDATIONS:
        if 'last_analysis' not in context.user_data:
            await query.message.reply_text("К сожалению, не найдены последние результаты анализов. Пожалуйста, загрузите анализы повторно.")
            return
        
        await query.message.reply_text("🔄 Генерирую рекомендации по питанию на основе ваших анализов...")
        
        try:
            recommendations = get_nutrition_recommendations(context.user_data['last_analysis'])
            await chunked_send_text(update, context, recommendations)
        except Exception as e:
            await query.message.reply_text("Извините, произошла ошибка при генерации рекомендаций. Попробуйте позже.")

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
    app.add_handler(CallbackQueryHandler(handle_recommendation_request))

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