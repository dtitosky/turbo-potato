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
                # Увеличиваем разрешение для лучшего качества
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("jpeg")
                base64_image = base64.b64encode(img_data).decode('utf-8')
                images_base64.append(base64_image)
            
            pdf_document.close()
            
            # Добавляем отладочный вывод
            print(f"Debug - PDF обработан, получено {len(images_base64)} страниц")
            
            # Формируем сообщения для каждой страницы
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
        # Для PDF берем первую страницу для проверки
        check_image = base64_image if not file_name.lower().endswith('.pdf') else images_base64[0]
        
        # Добавляем отладочный вывод
        print(f"Debug - Отправляем изображение на проверку, размер base64: {len(check_image)}")
        
        validation_response = openai.Client().chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Ты эксперт по медицинским анализам. Твоя задача - определить, является ли изображение анализом крови.
                    
                    Это анализ крови, если на изображении есть хотя бы один из следующих признаков:
                    - Показатели гемоглобина, эритроцитов, лейкоцитов
                    - Биохимические показатели крови
                    - Коагулограмма
                    - Общий анализ крови
                    - Любые другие лабораторные показатели крови
                    
                    Ответь строго 'да' или 'нет'. Если есть хоть один показатель крови - ответ 'да'."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Внимательно изучи изображение. Есть ли на нём хотя бы один показатель анализа крови?
                            Даже если изображение не очень четкое, но ты видишь структуру медицинского анализа и любые показатели крови - ответь 'да'.
                            Ответь строго одним словом: 'да' или 'нет'."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{check_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10
        )
        
        # Добавляем отладочный вывод
        print(f"Debug - Ответ валидации: {validation_response.choices[0].message.content}")
        
        is_blood_test = validation_response.choices[0].message.content.strip().lower()
        
        if is_blood_test != "да":
            return "К сожалению, загруженный файл не является анализом крови. Пожалуйста, загрузите корректный анализ крови."
        
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