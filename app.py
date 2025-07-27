import os
from flask import Flask, request
import requests
from groq import Groq
from dotenv import load_dotenv
from langdetect import detect

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "mixtral-8x7b-32768"

client = Groq(api_key=GROQ_API_KEY)

# भाषा ओळखून योग्य उत्तर द्या
def detect_language(text):
    try:
        lang = detect(text)
        if lang.startswith("mr"):
            return "Marathi"
        elif lang.startswith("hi"):
            return "Hindi"
        else:
            return "English"
    except:
        return "English"

def generate_reply(prompt, language):
    system_prompt = {
        "Marathi": "तू एक बुद्धिमान मराठी सहाय्यक आहेस. वापरकर्त्याच्या प्रश्नांना स्पष्ट मराठीत उत्तर दे.",
        "Hindi": "तुम एक बुद्धिमान हिंदी सहायक हो। उपयोगकर्ता के सवालों का स्पष्ट हिंदी में उत्तर दो।",
        "English": "You are a smart assistant. Answer the user's questions clearly in English."
    }[language]

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model=GROQ_MODEL
    )
    return chat_completion.choices[0].message.content

@app.route('/')
def home():
    return 'Smart AI Bot is running!'

@app.route('/webhook', methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"]["text"]
        user_lang = detect_language(user_msg)
        reply = generate_reply(user_msg, user_lang)

        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": reply})

    return "OK"