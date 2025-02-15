import os
import openai
import json
import requests
import base64
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF для работы с PDF

# Устанавливаем ключ OpenAI из переменных окружения
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY не установлен в переменных окружения")

def get_analysis_from_chatgpt(recognized_text: str) -> str:
    """
    Отправляет распознанный текст в OpenAI ChatCompletion и возвращает результат.
    Формат запроса (prompt) можно подстроить под нужный формат ответа.
    """
    prompt = f"""Проанализируй следующие данные анализа крови.

Требуемый формат ответа:
- Общий вывод.
- Рекомендации по питанию.
- Дополнительные комментарии.

Данные анализа:
{recognized_text}
"""
    try:
        response = openai.Client().chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты являешься экспертом в области анализа крови. Дай подробный и структурированный анализ данных."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT: {e}"

def get_analysis_from_chatgpt_vision(file_bytes: bytes, file_name: str) -> str:
    """
    Отправляет изображение в GPT-4 Vision API, проверяет валидность анализа крови
    и при положительном результате выдает структурированный анализ на русском языке.
    """
    try:
        # Проверяем расширение файла
        if file_name.lower().endswith('.pdf'):
            # Обработка PDF
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            
            # Собираем все страницы PDF в список изображений
            images_base64 = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("jpeg")
                base64_image = base64.b64encode(img_data).decode('utf-8')
                images_base64.append(base64_image)
            
            pdf_document.close()
            
            # Формируем сообщения для каждой страницы
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Это страница {i+1} из {len(images_base64)} анализа крови. Проанализируй все данные."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img}"
                            }
                        }
                    ]
                }
                for i, img in enumerate(images_base64)
            ]
        else:
            # Обработка обычного изображения
            image = Image.open(BytesIO(file_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Проанализируй это изображение анализа крови. Дай подробный анализ в следующем формате:\n1. Общий вывод\n2. Отклонения от нормы\n3. Рекомендации"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        
        # Сначала проверяем, является ли это анализом крови
        validation_response = openai.Client().chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты эксперт по медицинским анализам. Твоя задача - определить, является ли изображение анализом крови."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Проверь, является ли это изображение анализом крови. Ответь только 'да' или 'нет'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image if not file_name.lower().endswith('.pdf') else images_base64[0]}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10
        )
        
        is_blood_test = validation_response.choices[0].message.content.strip().lower()
        
        if is_blood_test != "да":
            return "К сожалению, загруженный файл не является анализом крови. Пожалуйста, загрузите корректный анализ крови."
        
        # Отправляем промежуточное сообщение через контекст
        if 'update' in locals() and 'context' in locals():
            await update.message.reply_text("✅ Анализ крови успешно распознан. Пожалуйста, подождите, идет подробный анализ данных...")
        
        # Если это анализ крови, получаем детальный анализ
        response = openai.Client().chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Ты опытный врач-лаборант. Проанализируй данные анализа крови и предоставь структурированный отчет 
                    на русском языке в следующем формате:
                    1. ОБЩЕЕ ЗАКЛЮЧЕНИЕ
                    2. ОТКЛОНЕНИЯ ОТ НОРМЫ (если есть)
                    3. ВОЗМОЖНЫЕ ПРИЧИНЫ ОТКЛОНЕНИЙ
                    4. РЕКОМЕНДАЦИИ
                    
                    Используй понятный язык, избегай сложных медицинских терминов."""
                }
            ] + messages,
            max_tokens=1000
        )
        
        analysis_result = response.choices[0].message.content
        
        # Форматируем финальный ответ
        return f"""РЕЗУЛЬТАТ АНАЛИЗА:

{analysis_result}

Примечание: Данный анализ является предварительным и не заменяет консультацию врача."""

    except Exception as e:
        print(f"Debug - Error details: {str(e)}")  # Добавляем отладочный вывод
        return f"Ошибка при обращении к GPT-4 Vision: {e}" 