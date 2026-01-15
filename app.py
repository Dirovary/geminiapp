from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)

def handle_chat(data):
    messages = data.get("messages", [])
    if not messages:
        return None, "No messages provided"

    parts = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("system", "user", "assistant"):
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
        data = response.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        return reply, None
    except Exception as e:
        return None, str(e)


@app.route("/v1beta/chat/completions", methods=["POST"])
def chat_completions_v1beta():
    reply, error = handle_chat(request.json)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({
        "id": "chatcmpl-gemini",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": reply
                },
                "finish_reason": "stop"
            }
        ]
    })


@app.route("/v1beta/models", methods=["GET"])
def models_v1beta():
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
