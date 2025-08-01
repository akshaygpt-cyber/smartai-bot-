from flask import Flask, request
import requests
import os
from groq import Groq
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "mixtral-8x7b-32768"

client = Groq(api_key=GROQ_API_KEY)

def search_web(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return "\n".join([r["title"] + ": " + r["href"] for r in results])

def ask_ai(query, search_info):
    prompt = f"""User asked: {query}
Here is some live web search information:
{search_info}

Based on this, give a helpful, short, and updated answer:"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Real-time search + AI Answer
        search_data = search_web(text)
        reply = ask_ai(text, search_data)

        send_message(chat_id, reply)
    return 'ok'

@app.route('/')
def index():
    return "🤖 SmartAI with Real-Time Search is Running!"

if __name__ == '__main__':
    app.run(debug=True)