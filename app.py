from googletrans import Translator

def multi_lang_reply(text):
    translator = Translator()
    marathi = translator.translate(text, dest='mr').text
    hindi = translator.translate(text, dest='hi').text
    english = translator.translate(text, dest='en').text
    return marathi, hindi, english

def main():
    print("बहुभाषी Chatbot मध्ये तुमचे स्वागत आहे!")
    print("मराठी, हिंदी, इंग्रजी भाषेत तुमचा संदेश उत्तर म्हणून येईल.")
    print("बंद करण्यासाठी 'exit' टाका.\n")
    
    while True:
        user_input = input("तुमचा संदेश: ")
        if user_input.strip().lower() == 'exit':
            print("Chatbot कार्यक्रम संपवत आहे.")
            break
        
        marathi, hindi, english = multi_lang_reply(user_input)
        
        print("\nChatbot चे उत्तर:")
        print(f"मराठी: {marathi}")
        print(f"हिंदी: {hindi}")
        print(f"इंग्रजी: {english}\n")

if __name__ == "__main__":
    main()
