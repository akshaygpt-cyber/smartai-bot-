from flask import Flask, request, jsonify
import requests
import os
from langdetect import detect
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise Exception("TELEGRAM_TOKEN किंवा GROQ_API_KEY .env मध्ये सेट करा!")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Telegram API base URL for sending messages
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route('/')
def home():
    return '✅ Smart AI Bot is Running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 400

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_message = data['message']['text']

        try:
            # Detect language (optional usage, can be used to tweak prompt if needed)
            lang = detect(user_message)

            # Create a prompt system message that suits the user language (optional)
            system_message = (
                "तू एक मदत करणारा AI आहेस जो मराठी, हिंदी आणि इंग्रजी भाषांमध्ये वापरकर्त्यांना त्यांच्या भाषेत उत्तर देतो."
            )

            # Call Groq LLM chat completions
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7,
            )

            bot_reply = response.choices[0].message.content.strip()

        except Exception as e:
            print("❌ Error in Groq API call:", e)
            bot_reply = "क्षमस्व! काहीतरी गडबड झाली आहे."

        # Send the bot reply back to Telegram chat
        payload = {
            'chat_id': chat_id,
            'text': bot_reply,
            "parse_mode": "HTML"
        }
        try:
            requests.post(TELEGRAM_API_URL, json=payload)
        except Exception as e:
            print("❌ Telegram API call error:", e)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)