
from googletrans import Translator

def multi_lang_reply(text):
    translator = Translator()
    
    marathi = translator.translate(text, dest='mr').text
    hindi = translator.translate(text, dest='hi').text
    english = translator.translate(text, dest='en').text
    
    return marathi, hindi, english

def main():
    print("तुमचे स्वागत आहे! Marathi, Hindi, English मध्ये उत्तर दिले जाईल.")
    while True:
        user_input = input("\nतुमचा संदेश टाका (बंद करायचे असल्यास 'exit' टाका): ")
        if user_input.lower() == 'exit':
            print("कार्यक्रम समाप्त करत आहे.")
            break
        
        marathi, hindi, english = multi_lang_reply(user_input)
        print(f"\nMarathi: {marathi}")
        print(f"Hindi: {hindi}")
        print(f"English: {english}")

if __name__ == "__main__":
    main()
