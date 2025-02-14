@@ async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Используем модель ChatGPT Vision для извлечения текста из фото
    from chatgpt_client import get_text_from_image_via_chatgpt_vision
    test_text = get_text_from_image_via_chatgpt_vision(file_bytes)
    if not test_text.strip():
        await update.message.reply_text("Не удалось распознать текст с изображения через ChatGPT Vision.")
        return
    # Отправляем пользователю именно тот текст, который вернула модель
    await update.message.reply_text(f"Распознанный текст:\n{test_text}")

@@ async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Используем модель ChatGPT Vision для извлечения текста из PDF
    document = update.message.document
    file_obj = await context.bot.get_file(document.file_id)
    file_bytes = await file_obj.download_as_bytearray()
    from chatgpt_client import get_text_from_image_via_chatgpt_vision
    test_text = get_text_from_image_via_chatgpt_vision(file_bytes)
    if not test_text.strip():
        await update.message.reply_text("Не удалось распознать текст с документа через ChatGPT Vision.")
        return
    # Отправляем распознанный текст пользователю
    await update.message.reply_text(f"Распознанный текст:\n{test_text}")