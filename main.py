from flask import Flask, request
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

def generate_reply(prompt):
    print("🔥 User Prompt:", prompt)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": """
तू एक मदत करणारा AI Chatbot आहेस. वापरकर्त्याशी त्याच्या भाषेत उत्तर दे — मराठी, हिंदी किंवा इंग्रजी.
कृपया गोपनीयता, कायदेशीरता आणि वापरकर्त्याच्या भाषेचा आदर राख.
"""},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=json_data)
        print("📩 Groq Response:", response.text)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Error:", str(e))
        return "Error generating reply. 😢"

@app.route("/")
def home():
    return "SmartAI Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📨 Telegram Update:", data)

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        reply = generate_reply(user_message)

        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": reply
        }

        try:
            response = requests.post(send_url, json=payload)
            print("📤 Telegram Response:", response.text)
            response.raise_for_status()
        except Exception as e:
            print("❌ Telegram Error:", str(e))

    return "OK"