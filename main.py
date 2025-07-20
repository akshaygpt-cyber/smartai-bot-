from flask import Flask, request
import requests
import wikipedia

app = Flask(__name__)

TELEGRAM_TOKEN = "7996807296:AAGz5O6gqJxzBgasopA7HRJ3TpZiPL1wpnk"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

wikipedia.set_lang("en")  # default

def generate_reply(text):
    text = text.lower()

    # Wikipedia logic
    if any(ch in text for ch in ('मराठी', 'हिंदी', 'संस्कृत')):
        if 'मराठी' in text:
            wikipedia.set_lang("mr")
            query = text.replace('मराठी', '').strip()
        elif 'हिंदी' in text:
            wikipedia.set_lang("hi")
            query = text.replace('हिंदी', '').strip()
        else:
            wikipedia.set_lang("sa")
            query = text.replace('संस्कृत', '').strip()

        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"📚 {query} विषयी:\n{summary}"
        except Exception:
            return "❌ माहिती मिळाली नाही. कृपया वेगळं keyword वापरा."

    # Default English Wikipedia
    try: