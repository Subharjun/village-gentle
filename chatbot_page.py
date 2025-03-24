import streamlit as st
import requests
from deep_translator import GoogleTranslator

# Mistral AI Config
MISTRAL_API_KEY = "Uvn5XeYrywt3lrGLAjRqxnNPMC4pSz6L"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Function to get response from Mistral AI
def get_mistral_response(prompt, language="en"):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post(MISTRAL_API_URL, json=data, headers=headers)
    if response.status_code == 200:
        answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

        # Translate response if needed
        if language != "en":
            answer = GoogleTranslator(source="en", target=language).translate(answer)

        return answer
    else:
        return f"Error: {response.status_code} - {response.text}"

# **Chatbot UI Function**
def chatbot_page():
    st.title("🌿 Smart Farming Chatbot")
    st.write("Ask any farming-related questions in your preferred language!")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 🌍 Expanded Global + Indian Language Support
    languages = {
        "English": "en",
        "Hindi (हिन्दी)": "hi",
        "Bengali (বাংলা)": "bn",
        "Tamil (தமிழ்)": "ta",
        "Telugu (తెలుగు)": "te",
        "Marathi (मराठी)": "mr",
        "Gujarati (ગુજરાતી)": "gu",
        "Kannada (ಕನ್ನಡ)": "kn",
        "Malayalam (മലയാളം)": "ml",
        "Punjabi (ਪੰਜਾਬੀ)": "pa",
        "Odia (ଓଡ଼ିଆ)": "or",
        "French (Français)": "fr",
        "Spanish (Español)": "es",
        "German (Deutsch)": "de",
        "Italian (Italiano)": "it",
        "Portuguese (Português)": "pt",
        "Chinese (中文)": "zh",
        "Japanese (日本語)": "ja",
        "Korean (한국어)": "ko",
        "Arabic (العربية)": "ar",
        "Turkish (Türkçe)": "tr",
        "Persian (فارسی)": "fa",
        "Swahili (Kiswahili)": "sw",
        "Hausa (Hausa)": "ha",
        "Amharic (አማርኛ)": "am",
    }
    selected_lang = st.sidebar.selectbox("🌍 Choose your language:", list(languages.keys()), index=0)
    lang_code = languages[selected_lang]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input box at the bottom
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Translate input to English if needed
        translated_input = GoogleTranslator(source=lang_code, target="en").translate(user_input) if lang_code != "en" else user_input

        # Store user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get response from Mistral AI
        bot_response = get_mistral_response(translated_input, lang_code)

        # Store bot message
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        # Display bot response
        with st.chat_message("assistant"):
            st.markdown(bot_response)
