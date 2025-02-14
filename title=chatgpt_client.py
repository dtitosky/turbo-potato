def truncate_text(text: str, max_chars: int = 5000) -> str:
    """
    Обрезает входной текст, если его длина превышает max_chars символов.
    """
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[Данные обрезаны для сокращения длины]"
    return text

@@ def get_analysis_from_chatgpt(recognized_text: str) -> str:
-    prompt = f"""Ниже приведён текст анализа крови, полученный посредством OCR:
-{recognized_text}
-
-Пожалуйста, проанализируй эти данные и сформируй структурированный отчёт с форматированием в Markdown. Для этого:
-1. Начни с заголовка уровня 2: "## Краткий структурированный анализ".
-2. Затем выведи раздел с названием, например, "**Анализ мочи:**", и перечисли ключевые показатели в виде маркированного списка. Для каждого показателя укажи его значение (если показатель отсутствует, напиши "не указано"). При наличии нормальных диапазонов добавь их в скобках.
-3. Добавь раздел "Вывод:" под списком, где кратко сформулируй общий результат анализа.
-Пожалуйста, не добавляй лишнего текста.
-"""
+    # Обрезаем текст, если он слишком длинный (уменьшаем лимит для предотвращения превышения контекста)
+    truncated_text = truncate_text(recognized_text, max_chars=2000)
+    prompt = f"""Ниже приведён текст анализа крови, полученный посредством OCR:
+{truncated_text}
+
+Пожалуйста, проанализируй эти данные и сформируй структурированный отчёт с форматированием в Markdown. Для этого:
+1. Начни с заголовка уровня 2: "## Краткий структурированный анализ".
+2. Затем выведи раздел с названием, например, "**Анализ мочи:**", и перечисли ключевые показатели в виде маркированного списка. Для каждого показателя укажи его значение (если показатель отсутствует, напиши "не указано"). При наличии нормальных диапазонов добавь их в скобках.
+3. Добавь раздел "Вывод:" под списком, где кратко сформулируй общий результат анализа.
+Пожалуйста, не добавляй лишнего текста.
+"""

@@ def get_recommendations_from_chatgpt(analysis_text: str) -> str:
-    prompt = f"""На основе следующего анализа данных анализа крови:
-{analysis_text}
-
-Дай подробные рекомендации по дальнейшим действиям, питанию и образу жизни. Особое внимание удели рекомендациям по питанию: добавь достаточное количество эмодзи (например, 🍏, 🥦, 🍽️, 🥗 и т.д.), чтобы сделать текст более легкочитаемым. Структурируй рекомендации в виде аккуратно оформленного списка.
-""" 
+    prompt = f"""На основе следующего анализа данных анализа крови:
{analysis_text}

Дай подробные рекомендации по дальнейшим действиям, питанию и образу жизни. Обрати особое внимание на секцию, посвящённую питанию: обязательно используй эмодзи для усиления визуальной привлекательности – например, перед рекомендациями по фруктам укажи 🍏, для овощей – 🥦, для приема пищи – 🍽️, а также добавляй другие релевантные эмодзи. Структурируй рекомендации в виде аккуратно оформленного списка, где каждый пункт начинается с эмодзи.
""" 

def get_text_from_image_via_chatgpt_vision(image_bytes: bytes) -> str:
    """
    Гипотетическая функция для извлечения текста из изображения с использованием ChatGPT Vision.
    На данный момент публичного API для ChatGPT Vision нет, поэтому эта функция является примером.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision",
            messages=[
                {"role": "system", "content": "Ты являешься экспертом по визуальному восприятию. Извлеки и верни текст, присутствующий на изображении."}
            ],
            # Гипотетический способ передачи изображения, который может отличаться
            files=[("image", image_bytes)]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка при извлечении текста с помощью ChatGPT Vision: {e}" 