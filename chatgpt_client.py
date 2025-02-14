import os
import openai

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
    Отправляет файл (изображение или PDF) напрямую в ChatGPT Vision и возвращает результат анализа.
    Внимание: данная функция использует гипотетический API-вызов `openai.ChatCompletion.create_vision`.
    Реальная реализация может отличаться, когда ChatGPT Vision будет доступен через официальный API.
    """
    try:
        response = openai.ChatCompletion.create_vision(
            model="gpt-4-vision",
            file={"data": file_bytes, "filename": file_name},
            messages=[
                {"role": "system", "content": "Ты являешься экспертом в области анализа медицинских изображений."},
                {"role": "user", "content": "Проанализируй прикрепленный файл с анализом крови и выдай подробный, структурированный ответ."}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT Vision: {e}" 