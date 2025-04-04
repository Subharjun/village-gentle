import streamlit as st

# ✅ Ensure this is the FIRST command in your script
st.set_page_config(page_title="Village Gentle", layout="wide", initial_sidebar_state="expanded")

# ✅ Ensure session state initializes properly (Prevents KeyErrors)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "skill_videos" not in st.session_state:
    st.session_state.skill_videos = None
if "business_advice" not in st.session_state:
    st.session_state.business_advice = None
if "loan_opportunities" not in st.session_state:
    st.session_state.loan_opportunities = None

# ✅ Now import all pages
from chatbot_page import chatbot_page  # 💬 Chatbot Page
from recommendation_page import recommendation_page  # 📋 Recommendations Page
from weather_advisory import weather_advisory  # 🌦️ Weather Advisory Page
from healthcare import healthcare_page  # 🏥 Healthcare Assistance
from economic_opportunities import economic_opportunities_page  # 📈 Economic Opportunities

# ✅ Ensure session state initializes properly (Fix for mobile issues)
if "skill_videos" not in st.session_state:
    st.session_state.skill_videos = None
if "business_advice" not in st.session_state:
    st.session_state.business_advice = None
if "loan_opportunities" not in st.session_state:
    st.session_state.loan_opportunities = None

# 🌿 **Toggle for Desktop/Mobile Mode**
st.sidebar.title("🖥️ Mode Selection")
mode = st.sidebar.radio("Select Mode:", ["🖥️ Desktop Mode", "📱 Mobile Mode"])

# ✅ Apply layout settings based on mode
if mode == "📱 Mobile Mode":
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 600px !important;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# 🌾 **App Title**
st.title("🌾 Village Gentle - Farmer's Companion")

# 📌 **Sidebar Navigation**
st.sidebar.title("🌿 Navigation")
option = st.sidebar.radio("Go to:", [
    "💬 Chatbot", 
    "📋 Recommendations", 
    "🌦️ Weather Advisory", 
    "🏥 Healthcare Assistance", 
    "📈 Economic Opportunities"
])

# 📍 **Page Routing**
if option == "💬 Chatbot":
    chatbot_page()

elif option == "📋 Recommendations":
    recommendation_page()

elif option == "🌦️ Weather Advisory":
    weather_advisory()

elif option == "🏥 Healthcare Assistance":
    healthcare_page()

elif option == "📈 Economic Opportunities":
    economic_opportunities_page()
