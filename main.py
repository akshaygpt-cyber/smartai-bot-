def generate_reply(prompt):
    print("🔥 User Prompt:", prompt)  # DEBUG

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are a helpful AI Assistant that replies in English, Hindi or Marathi depending on user language."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://api.groq.com/openai/chat/completions", headers=headers, json=json_data)
    
    print("📩 Groq Response:", response.text)  # DEBUG

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Sorry, I couldn't generate a response."