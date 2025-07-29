from flask import Flask, request
import requests
import os
from langdetect import detect
from groq import Groq
from PIL import Image
from sympy import sympify
from bs4 import BeautifulSoup
from newspaper import Article
from googletrans import Translator

# ENV variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Init
app = Flask(__name__)
client = Groq(api_key=GROQ_API_KEY)
translator = Translator()

# ✅ Home route for UptimeRobot
@app.route('/')
def home():
    return 'SmartAI Bot is running!'

# ✅ Webhook route
@app.route('/webhook', methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" not in data:
        return "No message", 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_input = message.get("text", "")

    # भाषेचा अंदाज
    try:
        lang = detect(user_input)
    except:
        lang = "en"

    # गणित सोल्यूशन
    if any(op in user_input for op in ["+", "-", "*", "/", "^"]):
        try:
            result = sympify(user_input)
            reply = f"उत्तर: {result}"
        except:
            reply = "गणित समजले नाही. कृपया पुन्हा लिहा."
    
    # बातम्या किंवा वेबसाईट लिंक process करणे
    elif user_input.startswith("http"):
        try:
            article = Article(user_input)
            article.download()
            article.parse()
            reply = f"📰 Title: {article.title}\n\n📝 Summary: {article.text[:1000]}"
        except:
            reply = "URL समजला नाही किंवा काही त्रुटी झाली."

    # AI उत्तर (Groq)
    else:
        prompt = user_input
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "तू एक उपयुक्त, अचूक आणि बहुभाषिक सहाय्यक आहेस."},
                    {"role": "user", "content": prompt}
                ]
            )
            response = completion.choices[0].message.content
            if lang != "en":
                response = translator.translate(response, dest=lang).text
            reply = response
        except:
            reply = "उत्तर देताना अडचण आली. पुन्हा प्रयत्न करा."

    # Telegram reply
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(telegram_url, json={"chat_id": chat_id, "text": reply})

    return "OK", 200