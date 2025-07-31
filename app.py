from flask import Flask, request, jsonify
from groq import Groq
from langdetect import detect
from googletrans import Translator
from sympy import sympify, simplify
from sympy.core.sympify import SympifyError
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
translator = Translator()

# Groq Client init
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Language names mapping
LANG_MAP = {
    'mr': 'mr',  # Marathi
    'hi': 'hi',  # Hindi
    'en': 'en',  # English
}

def detect_language(text):
    try:
        lang = detect(text)
        return LANG_MAP.get(lang, 'en')
    except:
        return 'en'

def solve_math_expression(expression):
    try:
        expr = sympify(expression)
        return str(simplify(expr))
    except SympifyError:
        return None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Smart गणित ChatBot API चालू आहे 🔥"}), 200

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("query", "")

    if not user_input:
        return jsonify({"error": "Query missing"}), 400

    lang = detect_language(user_input)

    # Sympy try
    sympy_result = solve_math_expression(user_input)
    if sympy_result:
        translated = translator.translate(f"उत्तर: {sympy_result}", dest=lang).text
        return jsonify({"result": translated, "method": "sympy"})

    # Else fallback to Groq LLaMA-3
    messages = [
        {
            "role": "system",
            "content": "तू एक बुद्धिमान गणित सहाय्यक आहेस. वापरकर्त्याचे प्रश्न मराठी, हिंदी किंवा इंग्रजी भाषेत असू शकतात. तू स्पष्ट आणि अचूक उत्तर देतोस, आणि गणित पद्धत देखील सांगतोस."
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    try:
        chat_completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages
        )
        answer = chat_completion.choices[0].message.content
        return jsonify({"result": answer, "method": "groq"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)