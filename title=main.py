from chatgpt_client import get_analysis_from_chatgpt, get_recommendations_from_chatgpt, is_blood_test, extract_text_from_file

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        test_text = extract_text_from_file(file_bytes)
    except Exception as e:
        await update.message.reply_text(f"Error processing file: {e}")
        return

    await chunked_send_text(update, context, f"Based on the uploaded test data, here is the brief analysis:\n\n{analysis_result}")
    await chunked_send_text(update, context, f"Recommendations for further actions, nutrition, and lifestyle:\n\n{recommendations}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        test_text = extract_text_from_file(file_bytes)
    except Exception as e:
        await update.message.reply_text(f"Error processing image: {e}")
        return 