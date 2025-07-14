import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "mixtral-8x7b-32768"

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

@app.route('/')
def home():
    return 'SmartAI Bot is Live!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_message = data['message']['text']

        ai_reply = get_groq_reply(user_message)

        reply_payload = {'chat_id': chat_id, 'text': ai_reply}
        requests.post(TELEGRAM_URL, json=reply_payload)
    return 'OK'

def get_groq_reply(user_message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=body)
    try:
        return response.json()["choices"][0]["message"]["content"].strip()
    except:
        return "क्षमस्व, काही त्रुटी आली. कृपया पुन्हा प्रयत्न करा."

if __name__ == "__main__":
    app.run(debug=True)
