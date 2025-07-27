from flask import Flask, request
import requests
import os
from langdetect import detect
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get tokens from .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Telegram API base URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Root route (for checking if bot is running)
@app.route('/')
def home():
    return '✅ Smart AI Bot is Running!'

# Webhook route for Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_message = data['message']['text']

        try:
            # Detect user message language
            lang = detect(user_message)

            # Create reply using Groq LLM
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "तू एक मदत करणारा AI आहेस जो मराठी, हिंदी आणि इंग्रजी भाषांमध्ये वापरकर्त्यांना त्यांच्या भाषेत उत्तर देतो."},
                    {"role": "user", "content": user_message}
                ]
            )

            bot_reply = response.choices[0].message.content.strip()

        except Exception as e:
            print("❌ Error:", e)
            bot_reply = "क्षमस्व! काहीतरी गडबड झाली आहे."

        # Send reply to Telegram
        payload = {
            'chat_id': chat_id,
            'text': bot_reply
        }
        requests.post(TELEGRAM_API_URL, json=payload)

    return 'OK'

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)