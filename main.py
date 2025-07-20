from flask import Flask, request
import requests
import wikipedia
import os

app = Flask(__name__)

wikipedia.set_lang("mr")  # Default: Marathi

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def detect_language(text):
    if any(ch in text for ch in "अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह"):
        return "mr"
    elif any(ch in text for ch in "क्या", "कैसे", "है"):
        return "hi"
    else:
        return "en"

def ask_groq(message, language):
    wikipedia.set_lang(language)
    try:
        summary = wikipedia.summary(message, sentences=2, auto_suggest=False)
        return summary
    except:
        pass
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": (
                "You are SmartAI, a helpful and polite assistant. "
                "Always reply strictly in the SAME language as the user's question. "
                "Never mix languages in one reply. "
                "Reply only in pure Marathi, pure Hindi (देवनागरी), or pure English as per the input. "
                "Keep responses short, friendly, and helpful."
            )},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }
    response = requests.post(GROQ_API_URL,
                             headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                                      "Content-Type": "application/json"},
                             json=data)
    return response.json()["choices"][0]["message"]["content"].strip()

@app.route("/")
def home():
    return "Smart AI Bot is Running!"

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    msg = request.json.get("message", {}).get("text", "")
    chat_id = request.json.get("message", {}).get("chat", {}).get("id")
    lang = detect_language(msg)
    reply = ask_groq(msg, lang)
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": reply}
    )
    return {"ok": True}