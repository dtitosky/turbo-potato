@@ def get_analysis_from_chatgpt(recognized_text: str) -> str:
-    prompt = f"""Ниже приведён текст анализа крови, полученный посредством OCR:
-{recognized_text}
-
-Пожалуйста, проанализируй данные и выведи их в структурированном виде. Выдели ключевые показатели (например: Гемоглобин, Глюкоза, Лейкоциты, Тромбоциты и т.д.) и представь результат в виде маркированного списка, где для каждого показателя указано его значение (если показатель отсутствует в данных, укажи "не указано"). Обязательно начни ответ со строки "Краткий структурированный анализ:".
-"""
+    prompt = f"""Ниже приведён текст анализа крови, полученный посредством OCR:
{recognized_text}

Пожалуйста, проанализируй эти данные и сформируй структурированный отчёт с форматированием в Markdown. Для этого:
1. Начни с заголовка уровня 2: "## Краткий структурированный анализ".
2. Затем выведи раздел с названием, например, "**Анализ мочи:**", и перечисли ключевые показатели в виде маркированного списка. Для каждого показателя укажи его значение (если показатель отсутствует, напиши "не указано"). При наличии нормальных диапазонов добавь их в скобках.
3. Добавь раздел "Вывод:" под списком, где кратко сформулируй общий результат анализа.
Пожалуйста, не добавляй лишнего текста.
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
-Дай подробные рекомендации по дальнейшим действиям, питанию и образу жизни. Особое внимание удели рекомендациям по питанию: добавь достаточное количество эмодзи (например, 🍏, 🥦, 🍽️, 🥗 и т.д.), чтобы сделать текст более легкочитаемым. Структурируй рекомендации в виде аккуратно оформленного списка.
-""" 
+    prompt = f"""На основе следующего анализа данных анализа крови:
{analysis_text}

Дай подробные рекомендации по дальнейшим действиям, питанию и образу жизни. Обрати особое внимание на секцию, посвящённую питанию: обязательно используй эмодзи для усиления визуальной привлекательности – например, перед рекомендациями по фруктам укажи 🍏, для овощей – 🥦, для приема пищи – 🍽️, а также добавляй другие релевантные эмодзи. Структурируй рекомендации в виде аккуратно оформленного списка, где каждый пункт начинается с эмодзи.
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