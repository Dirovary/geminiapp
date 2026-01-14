from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
    f"?key={GEMINI_API_KEY}"
)

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_message}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)

    data = response.json()

    try:
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply = "Ошибка ответа от модели."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run()
