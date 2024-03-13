# Import necessary libraries
import google.generativeai as genai

# Assuming 'Bard API' is a fictional API for demonstration purposes
# Replace 'YOUR_API_KEY' with your actual Bard API key
GOOGLE_API_KEY = ''

def start_aiconvo():
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    genai.configure(api_key=GOOGLE_API_KEY)


    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                generation_config=generation_config)

    convo = model.start_chat(history=[
    ])
    return convo

if __name__ == "__main__":
    convo = start_aiconvo()
    convo.send_message("Hello, how are you?")
    print(convo.last.text)
