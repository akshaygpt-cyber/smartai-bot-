from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # ✅ Load .env variables

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])  # ✅ Telegram Webhook URL
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        reply = generate_reply(user_message)

        # Send reply to Telegram
        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        requests.post(send_url, json=payload)

    return {"ok": True}

@app.route("/")  # ✅ Home route for Render
def home():
    return "✅ SmartAI Telegram Bot is Running!"

def generate_reply(user_message):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Reply in Marathi, Hindi, or English."},
            {"role": "user", "content": user_message}
        ]
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "❌ क्षमस्व, काहीतरी तांत्रिक अडचण आली आहे."

if __name__ == "__main__":
    app.run(debug=False)