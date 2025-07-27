from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_groq_reply(user_message):
    print("User Message:", user_message)  # Debug

    # ⚠️ Historical Topics Filter
    historical_keywords = ["गांधी", "महात्मा गांधी", "शिवाजी", "आंबेडकर", "Tilak", "भा. रा. आंबेडकर", "Bhagat Singh"]
    for word in historical_keywords:
        if word.lower() in user_message.lower():
            return "🔍 ही माहिती ऐतिहासिक व्यक्तिमत्त्वावर आधारित आहे. कृपया अधिक तपशील Wikipedia किंवा सरकारी स्रोतांवरून पाहा. तरीही मी थोडकं उत्तर देऊ शकतो, विचारू का?"

    # ✅ जर historical keyword नसेल, तर Groq API ला विचार
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    print("Groq Response:", response.text)  # Debug
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "माफ करा, सध्या उत्तर देता येत नाही."

@app.route('/')
def home():
    return "🤖 Smart AI Bot is Running!"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Received Data:", data)  # Debug

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        reply = get_groq_reply(user_message)
        send_message(chat_id, reply)
    else:
        print("❌ message किंवा text सापडलं नाही.")
    return "OK"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    print("Send message response:", response.text)

if __name__ == '__main__':
    app.run(debug=True)
