@@ async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Используем гипотетическую функцию для извлечения текста из изображения через ChatGPT Vision
        from chatgpt_client import get_text_from_image_via_chatgpt_vision
        test_text = get_text_from_image_via_chatgpt_vision(file_bytes)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке изображения через ChatGPT Vision: {e}")
        return 