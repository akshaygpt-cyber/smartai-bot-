# app.py

from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def detect_language(text):
    marathi_pattern = r'[\u0900-\u097F]'
    hindi_words = ['क्या', 'कैसे', 'है', 'कौन', 'नमस्ते']
    
    if re.search(marathi_pattern, text):
        return 'marathi'
    elif any(word in text for word in hindi_words):
        return 'hindi'
    else:
        return 'english'

def get_reply_from_groq(user_message, language):
    try:
        prompt = {
            "marathi": f"तू एक मराठी सहाय्यक आहेस. वापरकर्त्याचा प्रश्न: {user_message}",
            "hindi": f"तुम एक हिंदी सहायक हो। उपयोगकर्ता का प्रश्न: {user_message}",
            "english": f"You are an English assistant. User asked: {user_message}"
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt[language]}],
            "temperature": 0.7
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content'].strip()

    except Exception as e:
        return "क्षमस्व! काहीतरी गडबड झाली."

def send_message(chat_id, reply_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": reply_text
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
        language = detect_language(message)
        reply = get_reply_from_groq(message, language)
        send_message(chat_id, reply)
    except Exception as e:
        send_message(chat_id, "क्षमस्व! काहीतरी गडबड झाली.")
    return "OK"

@app.route("/")
def home():
    return "Smart AI ChatBot is Running!"