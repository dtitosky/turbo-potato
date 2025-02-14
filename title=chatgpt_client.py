import re

def clean_recognized_text(text: str) -> str:
    """
    Removes all sequences of the form (cid:number) from the text.
    If the resulting text is empty while the original text is not, returns the original text.
    """
    cleaned = re.sub(r'\(cid:\d+\)', ' ', text).strip()
    if not cleaned and text.strip():
        return text
    return cleaned

def get_analysis_from_chatgpt(recognized_text: str) -> str:
    cleaned_text = clean_recognized_text(recognized_text)
    prompt = f"""Below is the text of a blood test scan obtained via OCR:
{cleaned_text}

Please analyze this data and generate a structured report in Markdown format in English. To do this:
1. Start with a level 2 header: "## Brief Structured Analysis".
2. Output a section titled, for example, "**Analysis:**", and list only the key indicators that are present in the data as a bullet list. For each indicator, specify its value and, if available, the normal ranges in parentheses. Do not include indicators that are not present in the provided data.
3. Add a section titled "Conclusion:" below the list, where you briefly summarize the overall results based solely on the information in the text.
Please do not add any extraneous text. The response must be entirely in English.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in medical diagnostics. Deny a detailed and structured analysis of the data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

def get_recommendations_from_chatgpt(analysis_text: str) -> str:
    prompt = f"""Based on the following blood test analysis data:
{analysis_text}

Provide detailed recommendations for further actions, nutrition, and lifestyle. Format your answer in Markdown, where each item begins with an emoji. Pay special attention to the nutrition recommendations; for example:
- 🍏 before recommendations for fruits,
- 🥦 before recommendations for vegetables,
- 🍽️ before recommendations for meals,
- 💧 before recommendations for hydration,
and use other relevant emojis as needed.

Structure the recommendations as a neatly formatted list, with each item starting with the appropriate emoji. Please do not add any extraneous text.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in health and nutrition. Deny recommendations based on analysis data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

def is_blood_test(recognized_text: str) -> bool:
    cleaned_text = clean_recognized_text(recognized_text)
    prompt = f"""Determine whether the following text pertains to blood tests:
{cleaned_text}

If it is a blood test, reply with only one word "YES". If the text does not pertain to blood tests, reply with only one word "NO".
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in medical diagnostics. Answer strictly with one word: only 'YES' or 'NO'."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=10
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == "yes"

def extract_text_from_file(file_bytes: bytes) -> str:
    """
    Extracts text from the given file bytes using the GPT‑4 Vision model.
    """
    try:
        response = openai.Vision.create(
            model="gpt-4-vision",
            image=file_bytes,
        )
        # Предполагаем, что ответ содержит ключ "extracted_text" с распознанным текстом.
        extracted_text = response.get("extracted_text", "")
        return extracted_text
    except Exception as e:
        return f"Error extracting text: {e}"