import os
import openai
import json
import requests
import base64

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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты являешься экспертом в области анализа крови. Дай подробный и структурированный анализ данных."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT: {e}"

def get_analysis_from_chatgpt_vision(file_bytes: bytes, file_name: str) -> str:
    """
    Отправляет изображение в GPT-4 Vision API и получает анализ.
    """
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }
    
    # Кодируем изображение в base64
    encoded_image = base64.b64encode(file_bytes).decode('utf-8')
    
    # Формируем payload согласно документации OpenAI
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
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
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Проверяем статус ответа
        print("Debug - Response:", response.text)  # Добавляем отладочный вывод
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Debug - Error details: {str(e)}")  # Добавляем отладочный вывод
        return f"Ошибка при обращении к GPT-4 Vision: {str(e)}" 