from flask import Flask, request
import requests
import os

app = Flask(__name__)  # ✅ हे app object हवेच

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.route("/")
def home():
    return "SmartAI is Running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        reply = generate_reply(user_message)
        send_message(chat_id, reply)
    return "OK", 200

def generate_reply(prompt):
    print("🔥 User Prompt:", prompt)  # DEBUG

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are a helpful AI Assistant that replies in English, Hindi or Marathi depending on user language."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/chat/completions", headers=headers, json=json_data)
        print("📩 Groq Response:", response.text)  # DEBUG
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Error:", str(e))  # DEBUG
        return "Error generating reply. 😢"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)