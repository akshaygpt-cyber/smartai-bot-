
from googletrans import Translator

def multi_lang_reply(text):
    translator = Translator()
    
    # मराठी मध्ये अनुवाद
    marathi = translator.translate(text, dest='mr').text
    
    # हिंदी मध्ये अनुवाद
    hindi = translator.translate(text, dest='hi').text
    
    # इंग्रजी मध्ये अनुवाद (जर input इतर भाषेत असेल तर इंग्रजी reply)
    english = translator.translate(text, dest='en').text
    
    return {
        'marathi': marathi,
        'hindi': hindi,
        'english': english
    }

# Example
user_input = "How are you?"
replies = multi_lang_reply(user_input)
print("Marathi:", replies['marathi'])
print("Hindi:", replies['hindi'])
print("English:", replies['english'])
