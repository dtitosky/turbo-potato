@@ async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сначала передаём файл в модель Vision для извлечения текста (ChatGPT Vision)
    from chatgpt_client import get_text_from_image_via_chatgpt_vision
    test_text = get_text_from_image_via_chatgpt_vision(file_bytes)
    if not test_text.strip():
        await update.message.reply_text("Не удалось распознать текст с изображения через ChatGPT Vision.")
        return 