from chatgpt_client import get_analysis_from_chatgpt, get_recommendations_from_chatgpt, is_blood_test, extract_text_from_file

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        test_text = extract_text_from_file(file_bytes)
    except Exception as e:
        await update.message.reply_text(f"Error processing file: {e}")
        return

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        test_text = extract_text_from_file(file_bytes)
    except Exception as e:
        await update.message.reply_text(f"Error processing image: {e}")
        return 