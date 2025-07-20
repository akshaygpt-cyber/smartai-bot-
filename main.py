from flask import Flask, request
import requests
import wikipedia
import re

app = Flask(__name__)

TELEGRAM_TOKEN = "7996807296:AAGz5O6gqJxzBgasopA7HRJ3TpZiPL1wpnk"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def detect_script(text):
    # Detect Devanagari script (for Marathi/Hindi/Sanskrit)
    return bool(re.search(r'[\u0900-\u097F]', text))

def generate_reply(text):
    original_text = text
    text = text.lower()

    if 'मराठी' in text:
        wikipedia.set_lang("mr")
        query = text.replace('मराठी', '').strip()
    elif 'हिंदी' in text:
        wikipedia.set_lang("hi")
        query = text.replace('हिंदी', '').strip()
    elif 'संस्कृत' in text:
        wikipedia.set_lang("sa")
        query = text.replace('संस्कृत', '').strip()
    else:
        if detect_script(text):
            wikipedia.set_lang("mr")
        else:
            wikipedia.set_lang("en")
        query = original_text.strip()

    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"📖 {query} विषयी:\n{summary}"
    except Exception:
        return "❌ माहिती मिळाली नाही. कृपया वेगळं keyword वापरा."

@app.route('/', methods=['POST'])
def telegram_webhook():
    data = request.json
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_text = data['message']['text']
        reply = generate_reply(user_text)

        payload = {
            'chat_id': chat_id,
            'text': reply
        }
        requests.post(TELEGRAM_API_URL, json=payload)

    return 'ok'