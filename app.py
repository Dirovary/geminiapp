from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Берём API-ключ из переменных окружения Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # URL для Gemini 2.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    # Корректный формат запроса для Gemini
    payload = {
        "input_text": user_message,
        "temperature": 0.7,           # немного творчества
        "max_output_tokens": 500       # длина ответа
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        # Берём текст ответа
        reply = data.get("candidates", [])[0].get("content", {}).get("text", "Пустой ответ от модели.")
    except Exception as e:
        reply = f"Ошибка ответа от модели: {e}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run()
