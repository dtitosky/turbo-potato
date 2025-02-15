import requests
import json
import openai

def get_analysis_from_chatgpt_vision(file_bytes: bytes, file_name: str) -> str:
    # Гипотетический URL для ChatGPT Vision. Реальная реализация зависит от официального API.
    url = "https://api.openai.com/v1/chat/completions/vision"
    
    headers = {
        "Authorization": f"Bearer {openai.api_key}"
    }
    # Формируем поля для multipart-запроса:
    files = {
        "file": (file_name, file_bytes, "application/octet-stream"),
        "model": (None, "gpt-4-vision"),
        "messages": (None, json.dumps([
            {"role": "system", "content": "Ты являешься экспертом в области анализа медицинских изображений."},
            {"role": "user", "content": "Проанализируй прикрепленный файл с анализом крови и выдай подробный, структурированный ответ."}
        ])),
        "temperature": (None, "0.7"),
        "max_tokens": (None, "800")
    }
    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        rjson = response.json()
        return rjson["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT Vision: {e}" 