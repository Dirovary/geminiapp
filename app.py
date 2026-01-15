from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# ===================== НАСТРОЙКИ =====================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_ID = "gemini-2.5-flash"

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL_ID}:generateContent"
)

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def to_gemini_payload(messages):
    """Преобразуем OpenAI messages -> Gemini contents.parts"""
    parts = []
    for msg in messages:
        if msg.get("content"):
            parts.append({"text": msg["content"]})
    return {"contents": [{"parts": parts}]}

def openai_response(text):
    """Формат OpenAI-compatible для RikkaHub с usage"""
    return {
        "id": "chatcmpl-gemini",
        "object": "chat.completion",
        "created": 0,
        "model": MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

# ===================== CHAT COMPLETIONS =====================

@app.route("/v1/chat/completions", methods=["POST"])
@app.route("/v1beta/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json or {}
    messages = data.get("messages")
    
    if not messages:
        return jsonify({"error": "messages field required"}), 400

    try:
        # Отправляем запрос в Gemini API
        r = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=to_gemini_payload(messages),
            timeout=60
        )
        r.raise_for_status()
        reply = r.json()["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(openai_response(reply))

# ===================== MODELS =====================

@app.route("/v1/models", methods=["GET"])
@app.route("/v1beta/models", methods=["GET"])
def models():
    """Обязательный эндпоинт для RikkaHub"""
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "created": 0,
                "owned_by": "openai"
            }
        ]
    })

# ===================== DASHBOARD / CREDIT =====================
# Чтобы RikkaHub не ругался на баланс
@app.route("/v1/dashboard/billing/credit_grants", methods=["GET"])
@app.route("/v1beta/dashboard/billing/credit_grants", methods=["GET"])
def credit_grants():
    return jsonify({
        "object": "credit_grants",
        "total_granted": 1000000,
        "total_used": 0,
        "total_available": 1000000
    })

# ===================== RUN =====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
