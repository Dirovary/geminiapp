from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_ID = "gemini-2.5-flash"

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL_ID}:generateContent"
)

# ========= ВСПОМОГАТЕЛЬНО =========

def to_gemini_payload(messages):
    parts = []
    for m in messages:
        if m.get("content"):
            parts.append({"text": m["content"]})
    return {"contents": [{"parts": parts}]}

def openai_response(text):
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
        ]
    }

# ========= CHAT COMPLETIONS =========

@app.route("/v1/chat/completions", methods=["POST"])
@app.route("/v1beta/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json or {}
    messages = data.get("messages")

    if not messages:
        return jsonify({"error": "messages required"}), 400

    try:
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


# ========= MODELS (КЛЮЧЕВОЕ МЕСТО) =========

@app.route("/v1/models", methods=["GET"])
@app.route("/v1beta/models", methods=["GET"])
def models():
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


# ========= RUN =========

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
