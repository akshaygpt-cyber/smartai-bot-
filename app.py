import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from langdetect import detect
from googletrans import Translator
from sympy import sympify
from newspaper import Article
from PIL import Image
from io import BytesIO

# Load env variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = Flask(__name__)
translator = Translator()

# 🧠 GROQ API Function
def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.json()['choices'][0]['message']['content']

# 🔍 Try solving math expressions
def solve_math(query):
    try:
        expr = sympify(query)
        result = expr.evalf()
        return f"🔢 गणिताचं उत्तर: {result}"
    except:
        return None

# 🗞️ Live News from any link
def extract_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return f"📰 शीर्षक: {article.title}\n\n{article.text[:1000]}"
    except:
        return "❌ बातमी घेताना त्रुटी आली."

# 🌍 भाषा ओळख व भाषांतर
def detect_and_translate(text, target='en'):
    try:
        lang = detect(text)
        translated = translator.translate(text, dest=target)
        return translated.text
    except:
        return text

# 📷 फोटो Handle
def get_photo_url(file_id):
    res = requests.get(f"{TELEGRAM_URL}/getFile?file_id={file_id}").json()
    file_path = res['result']['file_path']
    return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

# 💬 Telegram Webhook Handler
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        reply = "❓ काही उत्तर मिळालं नाही."

        # Handle Photo
        if 'photo' in data['message']:
            file_id = data['message']['photo'][-1]['file_id']
            image_url = get_photo_url(file_id)
            reply = f"📷 फोटो मिळाला! पण कृपया प्रश्नसुद्धा लिहा.\n[Image]({image_url})"

        # Handle Text
        elif 'text' in data['message']:
            text = data['message']['text']
            lower_text = text.lower()

            # गणित
            math_result = solve_math(text)
            if math_result:
                reply = math_result
            # चालू घडामोडी लिंक दिल्यास
            elif "http" in text:
                reply = extract_article(text)
            # सामान्य प्रश्न - LLM ला पाठवा
            else:
                reply = ask_groq(text)

        # Send response
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply,
            "parse_mode": "Markdown"
        })

    return "ok"

# 🌐 Root Route
@app.route('/')
def index():
    return "🤖 AkshaySmartBot is Live!"