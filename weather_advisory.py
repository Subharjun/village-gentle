import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from deep_translator import GoogleTranslator

# ✅ API KEYS
MISTRAL_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxx"
WINDY_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxx"

# ✅ Manual Location Input
def get_user_location():
    st.write("### 📍 Enter Your Location for Accurate Weather Data")

    city = st.text_input("🏙️ City:", placeholder="Enter your city name")
    state = st.text_input("🗺️ State/Province:", placeholder="Enter your state/province")
    lat = st.number_input("🌐 Latitude:", format="%.6f")
    lon = st.number_input("🌐 Longitude:", format="%.6f")

    if city and state and lat and lon:
        st.success(f"✅ Using location: {city}, {state} ({lat}, {lon})")
        return {"city": city, "state": state, "latitude": lat, "longitude": lon}
    else:
        st.warning("⚠️ Please enter all fields to get accurate data.")
        return None

# ✅ Fetch Weather Data from Open-Meteo API
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"

    try:
        response = requests.get(url)
        data = response.json()
        if "hourly" in data and "daily" in data:
            return data
        else:
            st.error("⚠️ Weather data unavailable for this location.")
            return None
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# ✅ Get AI-Based Farming Insights from Mistral AI
def get_farming_insights(weather_data):
    prompt = f"""
    Analyze the following weather conditions and provide farming insights:
    - Max Temperature: {weather_data['daily']['temperature_2m_max'][0]}°C
    - Min Temperature: {weather_data['daily']['temperature_2m_min'][0]}°C
    - Total Rainfall: {weather_data['daily']['precipitation_sum'][0]}mm
    - Wind Speed: {weather_data['hourly']['wind_speed_10m'][0]} km/h

    Based on these conditions, suggest:
    1. Suitable crops to grow.
    2. Weather threats (flood, drought, storm).
    3. Best farming practices for the next week.
    """

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No insights available.")
    else:
        return "Error retrieving farming insights."

# ✅ Embed Windy Weather Map
def display_windy_map(lat, lon):
    windy_map_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=7&level=surface&overlay=wind&menu=true&message=true&marker=true&calendar=now&pressure=true&type=map&location=coordinates&detail=true&detailLat={lat}&detailLon={lon}&metricWind=default&metricTemp=default&radarRange=-1"

    st.write("### 🌍 Live Weather Forecast Map ")
    st.components.v1.iframe(windy_map_url, width=800, height=500)

# ✅ Weather Advisory Page
def weather_advisory():
    st.title("🌤️ Smart Weather Advisory for Farmers")

    # 🌍 Get User Location
    user_location = get_user_location()
    if not user_location:
        return  # Stop execution if no location is entered

    lat, lon = user_location["latitude"], user_location["longitude"]

    # ☁️ Fetch Weather Data
    weather_data = get_weather_data(lat, lon)

    if weather_data:
        st.write("### 📊 Weather Forecast Overview")

        # 📈 Display Temperature & Precipitation Trends
        hourly_time = pd.date_range(start=pd.Timestamp.now(), periods=24, freq="H")
        hourly_temp = weather_data["hourly"]["temperature_2m"][:24]
        hourly_precip = weather_data["hourly"]["precipitation"][:24]

        temp_df = pd.DataFrame({"Time": hourly_time, "Temperature (°C)": hourly_temp})
        precip_df = pd.DataFrame({"Time": hourly_time, "Precipitation (mm)": hourly_precip})

        fig_temp = px.line(temp_df, x="Time", y="Temperature (°C)", title="🌡️ Temperature Trend (Next 24 Hours)")
        fig_precip = px.bar(precip_df, x="Time", y="Precipitation (mm)", title="🌧️ Precipitation Forecast (Next 24 Hours)")

        st.plotly_chart(fig_temp)
        st.plotly_chart(fig_precip)

        # 🗺️ Display Windy Weather Forecast Map
        display_windy_map(lat, lon)

        # 🌾 Get AI-Powered Farming Insights
        st.write("### 🌾 AI-Powered Farming Advice")
        farming_advice = get_farming_insights(weather_data)
        st.info(farming_advice)
