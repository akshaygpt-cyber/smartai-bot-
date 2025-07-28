from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ✅ Home route for testing
@app.route('/')
def home():
    return 'SmartAI is Live ✅'

# ✅ Webhook route
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    chat_id = data["message"]["chat"]["id"]
    user_msg = data["message"]["text"]

    # News API handling
    if "बातमी" in user_msg.lower() or "news" in user_msg.lower():
        news = get_latest_news()
        reply = news if news else "क्षमस्व, सध्या बातम्या मिळू शकल्या नाहीत."
    else:
        reply = chat_with_groq(user_msg)

    send_message(chat_id, reply)
    return "OK"

# ✅ Function: Get latest news
def get_latest_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&language=mr&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json()["articles"][:3]
        return "\n\n".join([f"📰 {a['title']}\n{a['url']}" for a in articles])
    return None

# ✅ Function: Chat with Groq (LLaMA-3)
def chat_with_groq(user_msg):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": user_msg}]
    }
    res = requests.post(GROQ_API_URL, headers=headers, json=data)
    if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
    return "उत्तर मिळाले नाही. कृपया पुन्हा प्रयत्न करा."

# ✅ Function: Send message back to Telegram
def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(TELEGRAM_API_URL, json=payload)