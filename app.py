import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# ✅ Env Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ✅ Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# ✅ Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)

# ✅ Root Test Route for Render
@app.route("/", methods=["GET"])
def home():
    return "✅ Smart AI is Running!"

# ✅ Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        # News detection
        if "चालू घडामोडी" in user_message or "बातम्या" in user_message:
            reply = fetch_latest_news()
        else:
            reply = ask_groq(user_message)

        send_message(chat_id, reply)

    return "OK"

# ✅ Message sender
def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    requests.post(TELEGRAM_API_URL, json=payload)

# ✅ Groq reply function
def ask_groq(prompt):
    try:
        chat_completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "तू एक उपयुक्त मराठी, हिंदी आणि इंग्रजी भाषेत उत्तर देणारा स्मार्ट असिस्टंट आहेस."},
                {"role": "user", "content": prompt}
            ]
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"AI उत्तर देताना त्रुटी: {str(e)}"

# ✅ News fetcher
def fetch_latest_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        res = requests.get(url)
        articles = res.json().get("articles", [])[:5]

        if not articles:
            return "सध्या कोणतीही बातमी उपलब्ध नाही."

        news_list = [f"📰 {i+1}. {article['title']}" for i, article in enumerate(articles)]
        return "\n\n".join(news_list)

    except Exception as e:
        return f"बातम्या मिळवताना त्रुटी: {str(e)}"

# ✅ Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)