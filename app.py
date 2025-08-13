import os
import requests
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__)

def groq_chat(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }
    r = requests.post(url, headers=headers, json=data)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]
        reply = groq_chat(text)
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )
    return "ok"

@app.route("/")
def home():
    return "Puch AI Free Clone is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)