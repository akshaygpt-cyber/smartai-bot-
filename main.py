from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ENV variables (Render वर .env मध्ये ठेवले जातील)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Groq कडून reply मिळवण्याचं function
def generate_reply(user_message):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",  # GPT-3.5 quality
        "messages": [
            {"role": "system", "content": "You are a helpful multilingual assistant. You reply in Marathi, Hindi, or English depending on the question."},
            {"role": "user", "content": user_message}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "❌ माफ करा, काहीतरी चुकलंय. कृपया नंतर पुन्हा प्रयत्न करा."

# Telegram webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        # AI उत्तर मिळवा
        reply = generate_reply(user_message)

        # Telegram वर उत्तर पाठवा
        send_message_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        requests.post(send_message_url, json=payload)
        
    return {"ok": True}

# Render वर हे default home page
@app.route("/")
def home():
    return "✅ Smart AI ChatBot is Running!"

if __name__ == "__main__":
    app.run(debug=False)