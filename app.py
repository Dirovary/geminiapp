from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "prompt": {
            "messages": [
                {"author": "user", "content": [{"type": "text", "text": user_message}]}
            ]
        },
        "temperature": 0.7,
        "maxOutputTokens": 500
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        reply = data["candidates"][0]["content"][0]["text"]
    except Exception as e:
        reply = f"Ошибка ответа от модели: {e}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run()
