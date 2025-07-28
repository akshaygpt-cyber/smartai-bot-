import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# 🗝️ Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# 🔗 Telegram API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# 🤖 Groq Client Setup
groq_client = Groq(api_key=GROQ_API_KEY)

# 📡 Get Latest News (मराठीत)
def get_latest_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&language=mr&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])

    if not articles:
        return "माफ करा, सध्या कोणतीही बातमी उपलब्ध नाही."

    message = "🗞️ आजच्या महत्त्वाच्या बातम्या:\n\n"
    for article in articles[:5]:
        title = article.get("title", "")
        message += f"• {title}\n"

    return message.strip()

# 🧠 Get GPT-based reply
def generate_groq_reply(user_message):
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": user_message}],
        model="mixtral-8x7b-32768",
    )
    return chat_completion.choices[0].message.content

# 🚦 Webhook to receive Telegram messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        # 📰 News detection
        if any(word in user_message.lower() for word in ["घडामोडी", "बातमी", "news", "चालू"]:
            reply = get_latest_news()
        else:
            reply = generate_groq_reply(user_message)

        payload = {
            "chat_id": chat_id,
            "text": reply,
            "parse_mode": "Markdown"
        }