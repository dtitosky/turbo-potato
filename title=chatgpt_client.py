import re

def clean_recognized_text(text: str) -> str:
    """
    Удаляет из текста все последовательности вида (cid:число).
    Если после удаления текст оказывается пустым, возвращает исходный текст.
    """
    cleaned = re.sub(r'\(cid:\d+\)', ' ', text).strip()
    if not cleaned and text.strip():
        return text
    return cleaned

@@ def get_analysis_from_chatgpt(recognized_text: str) -> str:
    cleaned_text = clean_recognized_text(recognized_text)
    prompt = f"""Ниже приведён текст анализа крови, полученный посредством OCR:
{cleaned_text}

Пожалуйста, проанализируй эти данные и сформируй структурированный отчёт с форматированием в Markdown на русском языке. Для этого:
1. Начни с заголовка уровня 2: "## Краткий структурированный анализ".
2. Выведи раздел с названием, например, "**Анализ:**", и перечисли только те ключевые показатели, которые присутствуют в данных, в виде маркированного списка. Для каждого показателя укажи его значение и, если имеется, нормальные диапазоны в скобках. Не выводи показатели, которых нет в предоставленных данных.
3. Добавь раздел "Вывод:" под списком, где кратко сформулируй общий результат анализа, основываясь исключительно на информации из текста.
Пожалуйста, не добавляй лишнего текста. Ответ должен быть полностью на русском языке.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты являешься экспертом в области анализа крови. Дай подробный и структурированный анализ данных."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

@@ def get_recommendations_from_chatgpt(analysis_text: str) -> str:
-    prompt = f"""На основе следующего анализа данных анализа крови:
-{analysis_text}
-
-Дай подробные рекомендации по дальнейшим действиям, питанию и образу жизни. Обрати особое внимание на секцию, посвящённую питанию: обязательно используй эмодзи для усиления визуальной привлекательности – например, перед рекомендациями по фруктам укажи 🍏, для овощей – 🥦, для приема пищи – 🍽️, а также добавляй другие релевантные эмодзи. Структурируй рекомендации в виде аккуратно оформленного списка, где каждый пункт начинается с эмодзи.
-""" 
+    prompt = f"""На основе следующего анализа данных анализа крови:
{analysis_text}

Дай подробные рекомендации по дальнейшим действиям, питанию и образу жизни. Ответ сформируй в формате Markdown, где каждый пункт начинается с эмодзи. Особое внимание удели секции рекомендаций по питанию: обязательно используй эмодзи для усиления визуальной привлекательности – например:
- 🍏 перед рекомендациями по фруктам,
- 🥦 перед рекомендациями по овощам,
- 🍽️ перед рекомендациями по приему пищи,
- 💧 перед рекомендациями по гидратации,
а также используй другие релевантные эмодзи, где это необходимо.

Структурируй рекомендации в виде аккуратно оформленного списка, где каждый пункт начинается с соответствующего эмодзи. Пожалуйста, не добавляй лишнего текста.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты являешься экспертом по здоровью и питанию. Дай рекомендации на основе анализа данных."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

@@ def is_blood_test(recognized_text: str) -> bool:
    cleaned_text = clean_recognized_text(recognized_text)
    prompt = f"""Определи, относится ли следующий текст к анализам крови:
{cleaned_text}

Если это анализ крови, ответь только одним словом "ДА". Если текст не является анализом крови, ответь только одним словом "НЕТ".
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты эксперт в области медицинской диагностики. Отвечай строго одним словом: только 'ДА' или 'НЕТ'."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=10
    )