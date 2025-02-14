@@ async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем байты изображения
    from io import BytesIO
    file_obj = await context.bot.get_file(update.message.photo[-1].file_id)
    file_bytes = await file_obj.download_as_bytearray()

    # Используем модель ChatGPT Vision для прямого распознавания текста
    from chatgpt_client import get_text_from_image_via_chatgpt_vision
    test_text = get_text_from_image_via_chatgpt_vision(file_bytes)
    if not test_text.strip():
        await update.message.reply_text("Не удалось распознать текст с изображения через ChatGPT Vision.")
        return
    # Отправляем пользователю именно тот текст, который вернула модель
    await update.message.reply_text(f"Распознанный текст:\n{test_text}")

@@ async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Загружаем PDF-файл
    document = update.message.document
    file_obj = await context.bot.get_file(document.file_id)
    file_bytes = await file_obj.download_as_bytearray()

    # Используем модель ChatGPT Vision для прямого извлечения текста из PDF
    from chatgpt_client import get_text_from_image_via_chatgpt_vision
    test_text = get_text_from_image_via_chatgpt_vision(file_bytes)
    if not test_text.strip():
        await update.message.reply_text("Не удалось распознать текст с документа через ChatGPT Vision.")
        return
    # Отправляем пользователю распознанный текст
    await update.message.reply_text(f"Распознанный текст:\n{test_text}")