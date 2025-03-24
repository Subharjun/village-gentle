import streamlit as st
import requests

# ✅ API Keys (Directly included for development)
YOUTUBE_API_KEY = "AIzaSyCqEsmUIRhQbBTcEhJrA4eHbnldwbHS2Hk"
MISTRAL_API_KEY = "Uvn5XeYrywt3lrGLAjRqxnNPMC4pSz6L"
GOOGLE_API_KEY = "AIzaSyAu-1_wFQUy-LqWIN8gGBh70VbSHRvuD5k"
GOOGLE_CSE_ID = "071a9925363134f29"

# ✅ Ensure previous results persist across interactions
if "skill_videos" not in st.session_state:
    st.session_state.skill_videos = None
if "business_advice" not in st.session_state:
    st.session_state.business_advice = None
if "loan_opportunities" not in st.session_state:
    st.session_state.loan_opportunities = None

# 📚 **Fetch Educational Videos (YouTube API)**
def fetch_educational_videos(query):
    youtube_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=3&key={YOUTUBE_API_KEY}"
    try:
        response = requests.get(youtube_url)
        data = response.json()
        return data.get("items", [])
    except Exception:
        return []

# 🧠 **AI-Powered Business & Career Guidance (Mistral AI)**
def generate_ai_advice(prompt):
    mistral_url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 250
    }

    try:
        response = requests.post(mistral_url, json=body, headers=headers)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception:
        return "Error processing request."

# 💼 **Explore Business & Loan Opportunities (Google Custom Search)**
def search_business_loans(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    try:
        response = requests.get(search_url)
        data = response.json()
        return data.get("items", [])[:3]
    except Exception:
        return []

# 📌 **Skill Development & Economic Opportunities Page**
def economic_opportunities_page():
    st.title("📈 Skill Development & Economic Opportunities")

    # 📚 **Educational Videos**
    st.header("📚 Learn New Skills")
    topic = st.text_input("What do you want to learn?", key="skill_input")
    
    if st.button("Search Videos"):
        st.session_state.skill_videos = fetch_educational_videos(topic)

    # ✅ Display videos (Keep showing until new input)
    if st.session_state.skill_videos:
        for video in st.session_state.skill_videos:
            title = video["snippet"]["title"]
            video_id = video["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            st.video(video_url)
            st.write(f"🎥 **{title}**")

    # 🧠 **AI Business & Career Advice**
    st.header("🧠 AI-Powered Business & Career Advice")
    user_query = st.text_area("Ask for business or career advice:", key="business_input")

    if st.button("Get AI Advice"):
        st.session_state.business_advice = generate_ai_advice(user_query)

    # ✅ Display AI advice
    if st.session_state.business_advice:
        st.write(f"💡 **AI Advice:** {st.session_state.business_advice}")

    # 💰 **Explore Business & Loan Opportunities**
    st.header("💰 Explore Business & Loan Opportunities")
    loan_query = st.text_input("Search for funding sources, small business loans, or grants:", key="loan_input")

    if st.button("Search Opportunities"):
        st.session_state.loan_opportunities = search_business_loans(loan_query)

    # ✅ Display loan opportunities
    if st.session_state.loan_opportunities:
        for item in st.session_state.loan_opportunities:
            title = item.get("title", "No Title")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No description available.")
            st.write(f"🔹 **[{title}]({link})**")
            st.write(f"📌 {snippet}")

# ✅ Ensure seamless import into `main1.py`
if __name__ == "__main__":
    economic_opportunities_page()
