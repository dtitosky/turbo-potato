import os
import openai

# Получаем ключ OpenAI из переменных окружения.
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY не установлен в переменных окружения")

def get_analysis_from_chatgpt(recognized_text: str) -> str:
    """
    Отправляет распознанный текст в OpenAI ChatCompletion и возвращает результат.
    В prompt можно задать нужный вам формат ответа.
    """
    # Формируем запрос: можно подстроить под ваш формат.
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