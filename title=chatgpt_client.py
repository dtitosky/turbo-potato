import requests
import json
import openai
import base64

def get_analysis_from_chatgpt_vision(file_bytes: bytes, file_name: str) -> str:
    # Гипотетический URL для ChatGPT Vision. Реальная реализация зависит от официального API.
    url = "https://api.openai.com/v1/chat/completions/vision"
    
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }
    # Кодируем файл в base64
    encoded_file = base64.b64encode(file_bytes).decode("utf-8")
    
    # Формируем JSON‑payload с использованием ключей "prompt" и "image"
    payload = {
        "model": "gpt-4-vision",
        "prompt": "Проанализируй данное изображение анализа крови и выдай подробный, структурированный ответ.",
        "image": encoded_file,
        "temperature": 0.7,
        "max_tokens": 800
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        rjson = response.json()
        return rjson["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT Vision: {e}" 