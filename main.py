from flask import Flask, request
import requests
import wikipedia

app = Flask(__name__)

# Telegram Bot Token आणि URL
TELEGRAM_TOKEN = "7996807296:AAGz5O6gqJxzBgasopA7HRJ3TpZiPL1wpnk"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        reply = generate_reply(user_message)

        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        requests.post(TELEGRAM_API_URL, json=payload)

    return {"ok": True}

def generate_reply(text):
    text = text.strip()

    # भाषा ठरवा
    if text.startswith("मराठी:"):
        query = text.replace("मराठी:", "").strip()
        wikipedia.set_lang("mr")
    elif text.startswith("हिंदी:"):
        query = text.replace("हिंदी:", "").strip()
        wikipedia.set_lang("hi")
    else:
        query = text
        wikipedia.set_lang("en")

    # विकिपीडिया सर्च
    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"📖 {query} विषयी:\n{summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"❌ '{query}' विषयी अनेक लेख आहेत. कृपया अधिक स्पष्ट विचारा."
    except wikipedia.exceptions.PageError:
        return f"❌ '{query}' विषयाची माहिती सापडली नाही."
    except Exception:
        return "⚠️ काहीतरी चूक झाली. नंतर पुन्हा प्रयत्न करा."

# Health check route
@app.route("/", methods=["GET"])
def index():
    return "Smart AI Bot is live ✅"