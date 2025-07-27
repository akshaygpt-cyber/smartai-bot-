 from flask import Flask, request, jsonify
import requests
import os
import re
import ast
from langdetect import detect
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Tokens from .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise Exception("TELEGRAM_TOKEN किंवा GROQ_API_KEY .env मध्ये सेट करा!")

# Groq client init
client = Groq(api_key=GROQ_API_KEY)

# Telegram API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


@app.route('/')
def home():
    return '✅ Smart AI Bot is Running!'


# ✅ गणित expression आहे का ते तपासतो
def is_math_expression(text):
    return re.fullmatch(r'[\d\s\+\-\*/\.]+', text.strip()) is not None


# ✅ Safe गणित eval — कोणताही धोकादायक कोड चालणार नाही
def safe_eval(expr):
    try:
        tree = ast.parse(expr, mode='eval')
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp,
                                     ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div,
                                     ast.Pow, ast.Mod, ast.USub, ast.UAdd,
                                     ast.Load, ast.Constant)):
                raise ValueError("Unsafe expression")
        return eval(expr)
    except Exception:
        return None


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 400

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_message = data['message']['text']

        # 🧮 गणिती उदाहरण आहे का?
        if is_math_expression(user_message):
            result = safe_eval(user_message)
            if result is not None:
                bot_reply = f"उत्तर: {result}"
            else:
                bot_reply = "क्षमस्व! हे गणित समजलं नाही."
        else:
            try:
                lang = detect(user_message)

                # System Prompt