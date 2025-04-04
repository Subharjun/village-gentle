import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# ✅ API Keys (Directly included for development)
MISTRAL_API_KEY = "xxxxxxxxxxxxxxxxxxx"
GOOGLE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GOOGLE_CSE_ID = "xxxxxxxxxxxxxxxxxxxxx"
NUTRITIONIX_APP_ID = "xxxxxxxxxxxxxxxxx"
NUTRITIONIX_APP_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ORS_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
MISTRAL_URL = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 🔄 **Ensure all session state variables are initialized**
for key, default_value in {
    "ai_response": "",
    "healthcare_results": [],
    "recipe_response": "",
    "nutrition_response": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# 📍 **Find Nearby Healthcare Facilities**
def find_healthcare_facilities(location, query="general hospital"):
    search_query = f"{query} in {location}"
    google_url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"

    try:
        response = requests.get(google_url)
        data = response.json()
        return data.get("items", [])[:3] if "items" in data else []
    except:
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
        return data.get("features", [])[0]["geometry"]["coordinates"][::-1]  # Reverse order (lat, lon)
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
    except:
        return "Unable to process your request at the moment."

# 🍽 **Healthy Recipe Suggestions**
def get_healthy_recipes(ingredients):
    prompt = f"Suggest a healthy recipe using these ingredients: {ingredients}. Include ingredients, steps, and health benefits."
    return generate_ai_response(prompt)

# 🥗 **Smart Nutrition & Health Guide**
def get_nutrition_info(food_item):
    prompt = f"Classify '{food_item}' as either 'food' or 'condition'. Reply with ONLY 'food' or 'condition'."
    category = generate_ai_response(prompt).strip().lower().split()[0] if generate_ai_response(prompt) else ""

    if category == "condition":
        return generate_ai_response(f"What are the best 5 foods for {food_item}? Also, list 5 foods to avoid.")

    elif category == "food":
        nutritionix_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {"x-app-id": NUTRITIONIX_APP_ID, "x-app-key": NUTRITIONIX_APP_KEY, "Content-Type": "application/json"}
        body = {"query": food_item}

        try:
            response = requests.post(nutritionix_url, json=body, headers=headers)
            data = response.json()
            return data["foods"][0] if "foods" in data else "No nutritional data found."
        except:
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
    
    if st.session_state.get("ai_response"):
        st.write(f"🤖 *AI Response:*\n{st.session_state.ai_response}")

    # 📍 **Find Nearby Healthcare Facilities**
    st.header("📍 Find Nearby Healthcare Facilities")
    location = st.text_input("Enter your city or location:", key="location_input")
    special_need = st.text_input("Looking for a special type of clinic/hospital? (optional)", key="specialty_input")

    if st.button("Search Healthcare Facilities"):
        query = special_need if special_need else "general hospital"
        st.session_state.healthcare_results = find_healthcare_facilities(location, query)

    if st.session_state.get("healthcare_results"):
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

    if st.session_state.get("recipe_response"):
        st.write(f"🍛 *AI-Generated Recipe:*\n{st.session_state.recipe_response}")

    # 🥗 **Personalized Nutrition Information**
    st.header("🥗 Smart Nutrition & Health Guide")
    food_item = st.text_input("Enter a food item or health condition:", key="nutrition_input")

    if st.button("Get Nutrition Info"):
        st.session_state.nutrition_response = get_nutrition_info(food_item)

    if st.session_state.get("nutrition_response"):
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
