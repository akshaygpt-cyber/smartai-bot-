from flask import Flask, request
import requests
import wikipedia

app = Flask(__name__)

TELEGRAM_TOKEN = "7996807296:AAGz5O6gqJxzBgasopA7HRJ3TpZiPL1wpnk"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

wikipedia.set_lang("en")  # Default language

def generate_reply(text):
    text = text.lower()

    # Wikipedia logic for specific languages
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
    else:
        wikipedia.set_lang("en")
        try:
            summary = wikipedia.summary(text, sentences=2)
            return f"📖 About {text.title()}:\n{summary}"
        except Exception:
            return "❌ I couldn't find any information. Please try a different keyword."

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_text = data['message']['text']
        reply = generate_reply(user_text)

        payload = {
            'chat_id': chat_id,
            'text': reply
        }

        requests.post(TELEGRAM_API_URL, json=payload)

    return {'ok': True}

if __name__ == '__main__':
    app.run(debug=True)