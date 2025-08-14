#!/usr/bin/env python3

-- coding: utf-8 --

""" Marathi/Devanagari Q&A Telegram Bot (Flask + Groq)

Features

Answers user questions in clean Marathi (Devanagari) by default

Works with Telegram via webhook (Flask)

/start and /help commands

Simple, legal + privacy-friendly (no DB, no PII logging)


Env Vars (set these before running)

GROQ_API_KEY       : your Groq API key

TELEGRAM_BOT_TOKEN : your Telegram Bot token

WEBHOOK_SECRET     : a secret string to secure Telegram webhook (recommended)

PORT               : optional, defaults to 8000


Quick Start

1. pip install -U flask requests groq


2. python main.py --set-webhook https://YOUR-RENDER-APP.onrender.com/webhook


3. Run server: python main.py (Render auto-runs via gunicorn typically)



Notes

Default model set to "llama-3.1-70b-versatile" (update if needed).

If user writes in another language, bot replies in that language; otherwise Marathi. """


from future import annotations import os import sys import json import logging from typing import Any, Dict

import requests from flask import Flask, request, jsonify from groq import Groq

----------------------------

Basic config

----------------------------

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s") LOGGER = logging.getLogger("marathi-bot")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip() TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip() PORT = int(os.getenv("PORT", "8000"))

if not GROQ_API_KEY: LOGGER.warning("GROQ_API_KEY is not set. The bot will not be able to answer.") if not TELEGRAM_BOT_TOKEN: LOGGER.warning("TELEGRAM_BOT_TOKEN is not set. Webhook will not work.")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" MODEL_NAME = "llama-3.1-70b-versatile"  # update if your Groq account uses a different name

----------------------------

LLM Client

----------------------------

_groq_client: Groq | None = None

def get_groq_client() -> Groq: global _groq_client if _groq_client is None: _groq_client = Groq(api_key=GROQ_API_KEY) return _groq_client

SYSTEM_PROMPT = ( """ तू एक मदतनीस, अचूक AI सहाय्यक आहेस. नियम:

1. नेहमी डीफॉल्टने शुद्ध मराठी (देवनागरी लिपीत) उत्तर दे. शीर्षके/बुलेट्स/टेबल्स योग्य तेव्हा वापर.


2. जर वापरकर्त्याचा संदेश मराठीऐवजी दुसऱ्या भाषेत असेल, तर त्याच भाषेत संक्षिप्त आणि अचूक उत्तर दे; मात्र आवश्यक तांत्रिक शब्दांचे थोडक्यात मराठीत स्पष्टीकरण दे.


3. तथ्य पडताळून स्पष्ट, टप्प्याटप्प्याने मांड. अनावश्यक इंग्रजी शब्द टाळ.


4. थेट कॉपीराइटेड मजकूर देऊ नकोस; स्वतःच्या शब्दांत समजावून सांग.


5. उत्तर लहान ठेवू नको—पण मुद्देसूद ठेव. उदाहरणे, पायऱ्या, आणि आवश्यक तेथे टेबल/सूची दे. """ ).strip()



def generate_reply(user_text: str) -> str: """Call Groq LLM and return a Marathi (or user's language) reply.""" if not GROQ_API_KEY: return "🔧 कृपया सर्व्हरवर GROQ_API_KEY सेट करा."

client = get_groq_client()

try:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.4,
        max_tokens=1200,
        top_p=0.9,
        stream=False,
    )
    text = completion.choices[0].message.content.strip()
    # Light post-process: ensure something came back
    return text or "माफ करा, मला उत्तर तयार करता आले नाही. पुन्हा प्रयत्न करा."
except Exception as e:
    LOGGER.exception("Groq completion error: %s", e)
    return "⚠️ तांत्रिक अडचण आली आहे. थोड्या वेळाने पुन्हा प्रयत्न करा."

----------------------------

Telegram helpers

----------------------------

def tg_send_message(chat_id: int | str, text: str, reply_to_message_id: int | None = None) -> None: if not TELEGRAM_BOT_TOKEN: LOGGER.error("Missing TELEGRAM_BOT_TOKEN; cannot send message.") return payload: Dict[str, Any] = { "chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False, } if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id try: r = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=20) if r.status_code != 200: LOGGER.warning("Telegram sendMessage failed: %s - %s", r.status_code, r.text) except Exception as e: LOGGER.exception("Telegram sendMessage exception: %s", e)

def handle_command(text: str) -> str | None: t = (text or "").strip().lower() if t in ("/start", "/start@", "/help", "/help@") or t.startswith("/start") or t.startswith("/help"): return ( "नमस्कार! मी मराठी/देवनागरीत तुमच्या प्रश्नांची उत्तरे देणारा AI बॉट आहे.\n\n" "मला काहीही विचारा — इतिहास, गणित, प्रोग्रॅमिंग, परीक्षा तयारी, नोट्स, इ.\n" "\nकमान्डस्:\n• /start – ओळख\n• /help – मदत\n\n" "सूचना: डीफॉल्टने मी मराठीत उत्तर देतो. तुम्ही दुसऱ्या भाषेत विचारल्यास त्या भाषेतही उत्तर देईन." ) return None

----------------------------

Flask app + Webhook

----------------------------

app = Flask(name)

@app.get("/") def root() -> Any: return {"ok": True, "service": "Marathi/Devanagari QA Bot", "health": "green"}

@app.post("/webhook") def telegram_webhook() -> Any: # Optional: verify secret header if WEBHOOK_SECRET: secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "") if secret != WEBHOOK_SECRET: return jsonify({"ok": False, "error": "forbidden"}), 403

update = request.get_json(force=True, silent=True) or {}
LOGGER.debug("update: %s", json.dumps(update)[:2000])

message = update.get("message") or update.get("edited_message")
if not message:
    return jsonify({"ok": True})

chat = message.get("chat", {})
chat_id = chat.get("id")
message_id = message.get("message_id")
text = message.get("text", "").strip()

# Commands
cmd_reply = handle_command(text)
if cmd_reply:
    tg_send_message(chat_id, cmd_reply, reply_to_message_id=message_id)
    return jsonify({"ok": True})

# Normal Q&A
if text:
    reply = generate_reply(text)
    tg_send_message(chat_id, reply, reply_to_message_id=message_id)
else:
    tg_send_message(chat_id, "कृपया मजकूर संदेश पाठवा.", reply_to_message_id=message_id)

return jsonify({"ok": True})

----------------------------

Webhook setup helper

----------------------------

def set_webhook(url: str) -> None: if not TELEGRAM_BOT_TOKEN: LOGGER.error("TELEGRAM_BOT_TOKEN missing; cannot set webhook.") sys.exit(1)

data = {
    "url": url,
    # Pass secret so Telegram includes it in requests to your server
    "secret_token": WEBHOOK_SECRET or "",
    # Recommended: allow updates you actually use
    "allowed_updates": ["message", "edited_message"],
    "drop_pending_updates": True,
}
r = requests.post(f"{TELEGRAM_API}/setWebhook", json=data, timeout=20)
try:
    out = r.json()
except Exception:
    out = {"status": r.status_code, "text": r.text}
LOGGER.info("setWebhook response: %s", out)

----------------------------

Main entry

----------------------------

if name == "main": if len(sys.argv) >= 2 and sys.argv[1] == "--set-webhook": if len(sys.argv) < 3: print("Usage: python main.py --set-webhook https://YOUR-DOMAIN/webhook") sys.exit(1) set_webhook(sys.argv[2]) sys.exit(0)

app.run(host="0.0.0.0", port=PORT)

