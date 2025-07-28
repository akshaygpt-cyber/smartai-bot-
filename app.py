import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# 🔐 Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# 🤖 API Setup
groq_client = Groq(api_key=GROQ_API_KEY)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# 📰 Get latest news headlines
def get_latest_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "ok":
        headlines = [article["title"] for article in data["articles"][:5]]
        return "\n".join([f"🗞️ {title}" for title in headlines])
    else:
        return "सध्या चालू घडामोडी मिळाल्या नाहीत. नंतर पुन्हा प्रयत्न करा."

# 🧠 Generate response using LLaMA 3
def generate_llama_response(user_message):
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",  # ✅ LLaMA 3 वापरणे
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant that understands Marathi, Hindi, and English."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content.strip()

# 📩 Handle Telegram messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        # 👉 If message is about news
        if any(word in user_message.lower() for word in ["news", "चालू घडामोडी", "बातम्या", "खबरें"]):
            reply_text = get_latest_news()
        else:
            reply_text = generate_llama_response(user_message)

        # 📤 Send reply to Telegram
        requests.post(TELEGRAM_API_URL, json={
            "chat_id": chat_id,
            "text": reply_text
        })

    return "ok"

# 🏃 Run Flask app
if __name__ == "__main__":
    app.run(debug=True)