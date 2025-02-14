def analyze_blood_data(test_text: str) -> str:
    """
    Анализируем полученный текст и формируем рекомендации.
    Для упрощения делаем элементарную проверку ключевых слов.
    """
    recommendations = []

    # Схематичный пример:
    if "гемоглобин" in test_text.lower():
        recommendations.append("Гемоглобин замечен. Проверьте, не ниже ли нормы.")

    if "глюкоза" in test_text.lower():
        recommendations.append("У вас упоминается глюкоза. Возможно, стоит проверить уровень сахара.")

    # Питательные рекомендации (пример):
    recommendations.append("Общие советы: пейте больше воды, сбалансируйте питание (белки, жиры, углеводы).")

    # Формируем итоговый текст
    if not recommendations:
        return "Показателей для анализа не найдено, пожалуйста, уточните диапазоны."
    else:
        return "\n".join(recommendations) 