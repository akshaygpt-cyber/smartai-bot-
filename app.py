from flask import Flask, request
import requests, os
from langdetect import detect
from sympy import symbols, Eq, solve
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# गणित ओळखण्यासाठी साधी function
def solve_math_expression(text):
    try:
        x = symbols('x')
        if '=' in text:
            left, right = text.split('=')
            equation = Eq(eval(left), eval(right))
            solution = solve(equation)
            return f"x = {solution[0]}"
        else:
            return str(eval(text))
    except:
        return None

# भाषेवरून system_prompt ठरवणं
def get_prompt_by_language(language_code):
    if language_code == 'mr':
        return "तू एक उपयुक्त मराठी सहाय्यक आहेस."
    elif language_code == 'hi':
        return "तुम एक सहायक हिंदी एआई हो।"
    else:
        return "You are a helpful English AI Assistant."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        # गणितीय गणना आधी तपास
        math_answer = solve_math_expression(user_message)
        if math_answer:
            send_message(chat_id, f"📐 उत्तर: {math_answer}")
            return "ok"

        # भाषा शोधा
        language = detect(user_message)
        system_prompt = get_prompt_by_language(language)

        # AI कडून उत्तर घ्या
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        answer = response.choices[0].message.content
        send_message(chat_id, answer)

    return "ok"

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    requests.post(TELEGRAM_URL, json=payload)

@app.route("/", methods=["GET"])
def home():
    return "Smart AI ChatBot is Live ✅"