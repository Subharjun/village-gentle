import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load models and encoders
crop_model = joblib.load('crop_model.pkl')
fertilizer_model = joblib.load('fertilizer_model.pkl')
le_crop = joblib.load('le_crop.pkl')
le_soil = joblib.load('le_soil.pkl')

# Load Fertilizer Prediction Data
fertilizer_data = pd.read_csv('Fertilizer_Prediction.csv')

fertilizer_data.columns = fertilizer_data.columns.str.strip()

def recommendation_page():
    st.header("🌾 Crop & Fertilizer Recommendations")
    
    # Inputs Section
    st.subheader("🔍 Enter Input Values")
    N = st.number_input('🌾 Nitrogen (N in Kg/ha)', min_value=0.0, max_value=500.0, step=10.0)
    P = st.number_input('🌾 Phosphorus (P in Kg/ha)', min_value=0.0, max_value=50.0, step=1.0)
    K = st.number_input('🌾 Potassium (K in Kg/ha)', min_value=0.0, max_value=350.0, step=10.0)
    temperature = st.number_input('🌡️ Temperature (°C)', min_value=0.0, max_value=50.0, step=1.0)
    humidity = st.number_input('💧 Humidity (%)', min_value=0.0, max_value=100.0, step=1.0)
    ph = st.number_input('🧪 Soil pH', min_value=0.0, max_value=14.0, step=0.1)
    rainfall = st.number_input('🌧️ Rainfall (mm/year)', min_value=0.0, max_value=3000.0, step=50.0)
    
    crop_type = st.selectbox('🌱 Select Crop Type', le_crop.classes_)
    soil_type = st.selectbox('🪨 Select Soil Type', le_soil.classes_)

    if st.button("🔎 Predict Recommendations"):
        # Crop Prediction
        crop_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        crop_prediction = crop_model.predict(crop_data)
        st.subheader("🌾 Recommended Crop:")
        st.success(crop_prediction[0])

        # Fertilizer Recommendation - Priority to CSV Matching
        if 'Humidity' in fertilizer_data.columns:
            matching_row = fertilizer_data[
                (fertilizer_data['Temparature'] == temperature) &
                (fertilizer_data['Humidity'] == humidity) &
                (fertilizer_data['Soil Type'] == soil_type) &
                (fertilizer_data['Crop Type'] == crop_type) &
                (fertilizer_data['Nitrogen'] == N) &
                (fertilizer_data['Phosphorous'] == P) &
                (fertilizer_data['Potassium'] == K)
            ]

            if not matching_row.empty:
                fert_name = matching_row['Fertilizer Name'].values[0]
                st.subheader("💊 Recommended Fertilizer (From Dataset):")
            else:
                # Fallback to Model Prediction
                crop_type_encoded = le_crop.transform([crop_type])[0]
                soil_type_encoded = le_soil.transform([soil_type])[0]
                fert_data = np.array([[soil_type_encoded, crop_type_encoded, N, P, K]])
                fert_prediction = fertilizer_model.predict(fert_data)

                fertilizer_mapping = {
                    '20:20:0': 'Balanced NPK 20-20-0',
                    '10:26:26': 'High Phosphorus NPK 10-26-26',
                    '28:28': 'High Nitrogen NPK 28-28-0',
                    '17:17:17': 'Balanced NPK 17-17-17'
                }
                fert_name = fertilizer_mapping.get(fert_prediction[0], fert_prediction[0])
                st.subheader("💊 Recommended Fertilizer (From Model):")
            
            st.success(fert_name)
        else:
            st.error("🚨 Error: 'Humidity' column not found in Fertilizer_Prediction.csv. Please check the dataset.")

        # Recommendations and Warnings
        st.subheader("⚠️ Important Recommendations:")
        out_of_range = False
        if N > 480:
            st.warning("🔺 Nitrogen is too high. Consider planting leguminous crops or using organic manure.")
            out_of_range = True
        if P > 22:
            st.warning("🔺 Phosphorus is too high. Avoid phosphorus-rich fertilizers.")
            out_of_range = True
        if K > 280:
            st.warning("🔺 Potassium is too high. Use crops that uptake high potassium.")
            out_of_range = True
        if ph < 6.0:
            st.warning("🟠 Soil is too acidic. Use lime to increase pH.")
            out_of_range = True
        if ph > 8.5:
            st.warning("🟠 Soil is too alkaline. Use sulfur or organic compost.")
            out_of_range = True
        if temperature < 15:
            st.warning("❄️ Temperature is too low. Consider greenhouse farming to regulate temperature.")
            out_of_range = True
        if temperature > 35:
            st.warning("🔥 Temperature is too high. Ensure adequate irrigation and mulching.")
            out_of_range = True
        if humidity < 40:
            st.warning("💧 Humidity is too low. Use irrigation to increase moisture.")
            out_of_range = True
        if humidity > 70:
            st.warning("💨 Humidity is too high. Ensure proper ventilation to reduce fungal diseases.")
            out_of_range = True
        if rainfall < 500:
            st.warning("🌵 Rainfall is too low. Consider drought-resistant crops.")
            out_of_range = True
        if rainfall > 1500:
            st.warning("🌊 Rainfall is too high. Ensure proper drainage to prevent waterlogging.")
            out_of_range = True

        if out_of_range:
            st.warning("❗ For the given parameters, adjustments are recommended for optimal results.")

    # Helpful Tips Section
    st.header("💡 Helpful Tips and Recommendations")
    st.markdown("""
    ### 🌿 Input Ranges Reference
    - **Nitrogen (N):** Low (< 240), Medium (240-480), High (> 480) Kg/ha  
    - **Phosphorus (P):** Low (< 11), Medium (11-22), High (> 22) Kg/ha  
    - **Potassium (K):** Low (< 110), Medium (110-280), High (> 280) Kg/ha  
    - **pH Levels:** Acidic (< 6.0), Normal to Saline (6.0-8.5), Alkaline (> 9.0)  
    - **Temperature (°C):** Low (< 15), Medium (15-30), High (> 35)  
    - **Humidity (%):** Low (< 40), Medium (40-70), High (> 70)  
    - **Rainfall (mm/year):** Low (< 500), Medium (500-1500), High (> 1500)  

    ### 🌾 Optimization Tips
    1. **For high Nitrogen:** Use leguminous crops or organic manure.  
    2. **For high Phosphorus:** Avoid phosphorus-rich fertilizers.  
    3. **For high Potassium:** Use crops that uptake high potassium.  
    4. **To increase pH in acidic soils:** Apply lime.  
    5. **To decrease pH in alkaline soils:** Use sulfur or organic compost.  
    6. **For low temperatures:** Try greenhouse farming.  
    7. **For high temperatures:** Ensure proper irrigation and mulching.  
    8. **For low humidity:** Use irrigation to increase moisture.  
    9. **For high humidity:** Ensure proper ventilation to reduce fungal diseases.  
    10. **For low rainfall:** Choose drought-resistant crops.  
    11. **For high rainfall:** Ensure proper drainage.  
    """)

