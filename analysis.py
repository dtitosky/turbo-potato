def analyze_blood_data(test_text: str) -> str:
    """
    Выполняет локальный анализ распознанного текста анализа крови.
    В данном примере просто ищутся ключевые слова.
    """
    recommendations = []

    if "гемоглобин" in test_text.lower():
        recommendations.append("Гемоглобин: проверьте, не ниже ли нормы.")
    if "глюкоза" in test_text.lower():
        recommendations.append("Глюкоза: рекомендуем проверить уровень сахара.")

    # Общие советы
    recommendations.append("Общие советы: пейте больше воды, сбалансируйте питание (белки, жиры, углеводы).")

    return "\n".join(recommendations) if recommendations else "Показателей для анализа не найдено." 