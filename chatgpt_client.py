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
    prompt = f"""Ниже приведён текст анализа крови, полученный посредством OCR:
{recognized_text}

Пожалуйста, проанализируй данные и выведи их в структурированном виде. Выдели ключевые показатели (например: Гемоглобин, Глюкоза, Лейкоциты, Тромбоциты и т.д.) и представь результат в виде маркированного списка, где для каждого показателя указано его значение (если показатель отсутствует в данных, укажи "не указано"). Обязательно начни ответ со строки "Краткий структурированный анализ:".
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

def get_recommendations_from_chatgpt(analysis_text: str) -> str:
    """
    Передаёт полученный анализ данных в ChatGPT и возвращает подробные рекомендации.
    """
    prompt = f"""На основе следующего анализа данных анализа крови:
{analysis_text}

Дай подробные рекомендации по дальнейшим действиям, питанию и образу жизни.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты являешься экспертом по здоровью и питанию. Дай рекомендации на основе анализа данных."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT для рекомендаций: {e}"

def is_blood_test(recognized_text: str) -> bool:
    """
    Определяет, относится ли распознанный текст к анализам крови.
    Если текст содержит данные анализа крови, ответ должен быть «ДА».
    В противном случае — «НЕТ».
    """
    prompt = f"""Определи, относится ли следующий текст к анализам крови:
{recognized_text}

Если это анализ крови, ответь коротко "ДА", иначе ответь "НЕТ".
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты эксперт в области медицинской диагностики."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10
        )
        answer = response.choices[0].message.content.strip().lower()
        if "да" in answer:
            return True
        else:
            return False
    except Exception as e:
        return False 