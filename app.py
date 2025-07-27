
from flask import Flask, request
import os
import requests

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/")
def home():
    return "✅ SmartAI Multilingual Bot is Live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:
            reply = get_multilingual_reply(user_message)
            send_telegram_message(chat_id, reply)

    return "OK", 200

def get_multilingual_reply(message):
    prompt = f"""
तू एक हुशार बहुभाषिक सहायक आहेस. युजरचा प्रश्न ज्या भाषेत विचारलेला आहे, त्याच भाषेत उत्तर दे:
मराठी, हिंदी किंवा इंग्रजी.
प्रश्न: {message}
उत्तर:
"""
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return "क्षमस्व! काहीतरी गडबड झाली."

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run()