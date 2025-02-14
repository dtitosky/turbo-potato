from chatgpt_client import get_analysis_from_chatgpt, get_recommendations_from_chatgpt, is_blood_test, extract_text_from_file

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file_obj = await context.bot.get_file(document.file_id)
    file_bytes = await file_obj.download_as_bytearray()
    try:
        test_text = extract_text_from_file(file_bytes)
    except Exception as e:
        await update.message.reply_text(f"Error processing file: {e}")
        return

    # 1. Send recognized (OCR) text as first message
    await chunked_send_text(update, context, f"Recognized Text (OCR result):\n\n{test_text}")

    # 2. Check if text was recognized and belongs to a blood test
    if not test_text.strip():
        await update.message.reply_text("No text recognized from the uploaded file. Please upload a clearer file.")
        return

    if not is_blood_test(test_text):
        await update.message.reply_text("The uploaded file does not seem to contain blood test data. Please upload a proper blood test.")
        return

    # 3. Get analysis and recommendations
    analysis_result = get_analysis_from_chatgpt(test_text)
    recommendations = get_recommendations_from_chatgpt(analysis_result)

    # 4. Send analysis and recommendations as separate messages
    await chunked_send_text(update, context, f"Based on the uploaded test data, here is the brief analysis:\n\n{analysis_result}")
    await chunked_send_text(update, context, f"Recommendations for further actions, nutrition, and lifestyle:\n\n{recommendations}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]  # выбираем самое большое фото
    file_obj = await context.bot.get_file(photo.file_id)
    file_bytes = await file_obj.download_as_bytearray()
    try:
        test_text = extract_text_from_file(file_bytes)
    except Exception as e:
        await update.message.reply_text(f"Error processing image: {e}")
        return

    # 1. Send recognized (OCR) text as first message
    await chunked_send_text(update, context, f"Recognized Text (OCR result):\n\n{test_text}")

    # 2. Check if text was recognized and belongs to a blood test
    if not test_text.strip():
        await update.message.reply_text("No text recognized from the uploaded image. Please upload a clearer image.")
        return

    if not is_blood_test(test_text):
        await update.message.reply_text("The uploaded image does not seem to contain blood test data. Please upload a proper blood test.")
        return

    # 3. Get analysis and recommendations
    analysis_result = get_analysis_from_chatgpt(test_text)
    recommendations = get_recommendations_from_chatgpt(analysis_result)

    # 4. Send analysis and recommendations as separate messages
    await chunked_send_text(update, context, f"Based on the uploaded test data, here is the brief analysis:\n\n{analysis_result}")
    await chunked_send_text(update, context, f"Recommendations for further actions, nutrition, and lifestyle:\n\n{recommendations}")

async def chunked_send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    # Этот пример делит длинный текст на части, чтобы каждая не превышала 4096 символов
    chunk_size = 4096
    for i in range(0, len(text), chunk_size):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text[i:i+chunk_size]
        ) 