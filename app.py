from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# ====== НАСТРОЙКИ ======

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{GEMINI_MODEL}:generateContent"
)

# ====== ВСПОМОГАТЕЛЬНАЯ ЛОГИКА ======

def openai_messages_to_gemini(messages):
    """
    OpenAI messages -> Gemini contents.parts
    """
    parts = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("system", "user", "assistant"):
            parts.append({"text": content})
    return {
        "contents": [
            {
                "parts": parts
            }
        ]
    }


# ====== API ENDPOINTS ======

@app.route("/v1beta/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json or {}

    messages = data.get("messages")
    if not messages:
        return jsonify({"error": "messages is required"}), 400

    payload = openai_messages_to_gemini(messages)

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        gemini_data = response.json()

        reply_text = (
            gemini_data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 🔁 OpenAI-compatible response (МИНИМАЛЬНО, как любит RikkaHub)
    return jsonify({
        "id": "chatcmpl-gemini",
        "object": "chat.completion",
        "created": 0,
        "model": GEMINI_MODEL,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": reply_text
                },
                "finish_reason": "stop"
            }
        ]
    })


@app.route("/v1beta/models", methods=["GET"])
def list_models():
    """
    КРИТИЧЕСКИ важно для RikkaHub:
    - object = list
    - data = array
    - owned_by = openai
    - created = int
    """
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": GEMINI_MODEL,
                "object": "model",
                "created": 0,
                "owned_by": "openai"
            }
        ]
    })


# ====== ЗАПУСК ======

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
