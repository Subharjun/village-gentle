import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# ✅ API Keys (Directly included for development)
MISTRAL_API_KEY = "Uvn5XeYrywt3lrGLAjRqxnNPMC4pSz6L"
GOOGLE_API_KEY = "AIzaSyAu-1_wFQUy-LqWIN8gGBh70VbSHRvuD5k"
GOOGLE_CSE_ID = "071a9925363134f29"
NUTRITIONIX_APP_ID = "10620010"
NUTRITIONIX_APP_KEY = "6d54de36f4faa357b0b7fc9903144eb1"
ORS_API_KEY = "5b3ce3597851110001cf62488cd4fbecec9c49e9a0bc554fc2f98516"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

# 🔄 Initialize session state
if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""
if "healthcare_results" not in st.session_state:
    st.session_state.healthcare_results = []
if "recipe_response" not in st.session_state:
    st.session_state.recipe_response = ""
if "nutrition_response" not in st.session_state:
    st.session_state.nutrition_response = ""

# 📍 **Find Nearby Healthcare Facilities**
def find_healthcare_facilities(location, query="general hospital"):
    search_query = f"{query} in {location}"
    google_url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"

    try:
        response = requests.get(google_url)
        data = response.json()
        results = data.get("items", [])

        return results[:3] if results else []
    
    except Exception:
        return []

# 📌 **Generate Google Maps Link**
def generate_google_maps_link(place_name):
    return f"https://www.google.com/maps/search/?api=1&query={place_name.replace(' ', '+')}"

# 🗺 **Get Coordinates using OpenRouteService**
def get_location_coordinates(place_name):
    url = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&text={place_name}"
    
    try:
        response = requests.get(url)
        data = response.json()
        coordinates = data.get("features", [])[0]["geometry"]["coordinates"]
        return coordinates[::-1]  # Reverse order (lat, lon)
    except:
        return None

# 🗺 **Generate Interactive Map for Each Hospital**
def generate_map(hospital_name):
    coordinates = get_location_coordinates(hospital_name)
    if coordinates:
        lat, lon = coordinates
        map_ = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup=hospital_name, tooltip="Click for details").add_to(map_)
        return map_
    return None

# 🧠 **AI-Powered Healthcare Assistant**
def generate_ai_response(prompt):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    body = {"model": "mistral-medium", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200}

    try:
        response = requests.post(MISTRAL_URL, json=body, headers=headers)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except Exception:
        return "Unable to process your request at the moment."

# 🍽 **Healthy Recipe Suggestions**
def get_healthy_recipes(ingredients):
    prompt = f"Suggest a healthy recipe using these ingredients: {ingredients}. Include ingredients, steps, and health benefits."
    return generate_ai_response(prompt)

# 🥗 **Smart Nutrition & Health Guide**
def get_nutrition_info(food_item):
    prompt = f"Classify '{food_item}' as either 'food' or 'condition'. Reply with ONLY 'food' or 'condition'."
    category = generate_ai_response(prompt).strip().lower()

    category = category.split()[0] if category else ""

    if category == "condition":
        advice_prompt = f"What are the best 5 foods for {food_item}? Also, list 5 foods to avoid."
        return generate_ai_response(advice_prompt)

    elif category == "food":
        nutritionix_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {"x-app-id": NUTRITIONIX_APP_ID, "x-app-key": NUTRITIONIX_APP_KEY, "Content-Type": "application/json"}
        body = {"query": food_item}

        try:
            response = requests.post(nutritionix_url, json=body, headers=headers)
            data = response.json()
            return data["foods"][0] if "foods" in data else "No nutritional data found."
        
        except Exception:
            return "Error fetching nutrition data."

    else:
        return "I couldn't determine if this is a food or condition. Try again!"

# 📌 **Healthcare Page**
def healthcare_page():
    st.title("🏥 Healthcare Assistance")

    # 🧠 **AI-Powered Healthcare Assistant**
    st.header("🧠 AI-Powered Healthcare Assistant")
    user_query = st.text_input("Ask a health-related question:", key="ai_input")
    if st.button("Get Advice"):
        if user_query:
            st.session_state.ai_response = generate_ai_response(user_query)
    
    if st.session_state.ai_response:
        st.write(f"🤖 *AI Response:*\n{st.session_state.ai_response}")

    # 📍 **Find Nearby Healthcare Facilities**
    st.header("📍 Find Nearby Healthcare Facilities")
    location = st.text_input("Enter your city or location:", key="location_input")
    special_need = st.text_input("Looking for a special type of clinic/hospital? (optional)", key="specialty_input")

    if st.button("Search Healthcare Facilities"):
        query = special_need if special_need else "general hospital"
        st.session_state.healthcare_results = find_healthcare_facilities(location, query)

    if st.session_state.healthcare_results:
        for item in st.session_state.healthcare_results:
            title = item.get('title', 'No Title')
            link = generate_google_maps_link(title)
            summary = generate_ai_response(f"Summarize this hospital: {title}")

            st.write(f"🔹 *{title}* 🏥")
            st.markdown(f"[📌 View on Google Maps]({link})")
            st.write(f"📝 *Summary:* {summary}")

            # Display interactive map for this hospital
            map_ = generate_map(title)
            if map_:
                folium_static(map_)
            st.write("---")

    # 🍽 **Healthy Recipe Suggestions**
    st.header("🍽 Healthy Recipe Suggestions")
    ingredients = st.text_input("Enter ingredients (comma-separated):", key="recipe_input")

    if st.button("Get Recipes"):
        st.session_state.recipe_response = get_healthy_recipes(ingredients)

    if st.session_state.recipe_response:
        st.write(f"🍛 *AI-Generated Recipe:*\n{st.session_state.recipe_response}")

    # 🥗 **Personalized Nutrition Information**
    st.header("🥗 Smart Nutrition & Health Guide")
    food_item = st.text_input("Enter a food item or health condition:", key="nutrition_input")

    if st.button("Get Nutrition Info"):
        st.session_state.nutrition_response = get_nutrition_info(food_item)

    if st.session_state.nutrition_response:
        if isinstance(st.session_state.nutrition_response, dict):
            nutrition_data = st.session_state.nutrition_response
            st.write(f"🍏 *Food:* {nutrition_data.get('food_name', 'Unknown')}")
            st.write(f"📊 *Calories:* {nutrition_data.get('nf_calories', 'N/A')} kcal")
            st.write(f"💪 *Protein:* {nutrition_data.get('nf_protein', 'N/A')} g")
        else:
            st.error(st.session_state.nutrition_response)

# Run the healthcare page
if __name__ == "__main__":
    healthcare_page()
