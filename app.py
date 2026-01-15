from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json

    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    # 🔁 OpenAI messages → Gemini contents
    parts = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("user", "system"):
            parts.append({"text": content})

    payload = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        gemini_data = response.json()

        reply_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 🧠 OpenAI-compatible response
    return jsonify({
        "id": "chatcmpl-gemini",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": reply_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    })


@app.route("/v1/models", methods=["GET"])
def list_models():
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": "gemini-2.5-flash",
                "object": "model",
                "owned_by": "google"
            }
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
