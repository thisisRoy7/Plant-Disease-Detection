import streamlit as st
import tensorflow as tf
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="AgriGuard | Plant Disease Detection",
    page_icon="🌿",
    layout="wide",
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
    }
    .result-card {
        padding: 25px;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 8px solid #2E7D32;
    }
    .report-text {
        color: #444;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Prediction Logic ---
@st.cache_resource
def load_my_model():
    # Cache the model so it only loads once
    return tf.keras.models.load_model('trained_model.h5')

def model_prediction(test_image):
    model = load_my_model()
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr]) 
    prediction = model.predict(input_arr)
    return np.argmax(prediction)

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=80)
    st.title("AgriGuard AI")
    app_mode = st.selectbox("Navigation", ["Home", "About project", "Disease Recognition"])

# --- Data Mapping ---
CLASS_NAMES = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']

# Dictionary for professional descriptions
DISEASE_INFO = {
    "Healthy": {
        "description": "The plant shows no signs of visible disease. Continue regular watering and sunlight schedules.",
        "action": "Maintain current nutrient balance and monitor for seasonal pests."
    },
    "Bacterial Spot": {
        "description": "Small, water-soaked spots appear on leaves. Often caused by high humidity and infected seeds.",
        "action": "Remove infected leaves. Avoid overhead watering and apply a copper-based bactericide."
    },
    "Late Blight": {
        "description": "A serious fungal disease that causes dark, water-soaked patches on leaves and stems.",
        "action": "Improve air circulation. Destroy infected plants immediately to prevent the spread of spores."
    },
    "Default": {
        "description": "The system has detected signs of localized infection or fungal growth typical for this species.",
        "action": "Isolate the plant, remove affected foliage, and consult a local agricultural specialist."
    }
}

def get_report_details(disease_name):
    # Match disease to our dictionary or provide default
    for key in DISEASE_INFO.keys():
        if key.lower() in disease_name.lower():
            return DISEASE_INFO[key]
    return DISEASE_INFO["Default"]

# --- Home Page ---
if app_mode == "Home":
    st.title("🌿 Plant Disease Recognition System")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Precision Diagnostics for Smarter Farming
        Welcome to the **AgriGuard AI** platform. Our system helps farmers and enthusiasts 
        diagnose plant health issues instantly using computer vision.
        
        #### Quick Start Guide:
        - 📂 **Step 1:** Upload a clear photo of a single leaf.
        - ⚙️ **Step 2:** Click 'Analyze' to run the neural network.
        - 📋 **Step 3:** Review the health report and recommended actions.
        """)
        
    with col2:
        st.image("https://cdn.pixabay.com/photo/2018/01/26/08/13/agriculture-3108044_1280.jpg", use_column_width=True)

# --- Recognition Page ---
elif app_mode == "Disease Recognition":
    st.header("🔬 Disease Analysis")
    
    upload_col, preview_col = st.columns(2)
    
    with upload_col:
        st.subheader("Upload Leaf Image")
        test_image = st.file_uploader("Upload JPG/PNG format:", type=["jpg", "jpeg", "png"])
        predict_btn = st.button("Analyze Image")

    with preview_col:
        if test_image:
            st.image(test_image, width=350, caption="Uploaded Image")

    if predict_btn and test_image:
        with st.spinner("Decoding leaf patterns..."):
            idx = model_prediction(test_image)
            raw_name = CLASS_NAMES[idx]
            
            # Formatting for the UI
            plant_part = raw_name.split('___')[0].replace('_', ' ').title()
            disease_part = raw_name.split('___')[1].replace('_', ' ').title()
            
            report = get_report_details(disease_part)
            
            st.markdown("---")
            # The Professional Results Display
            st.markdown(f"""
                <div class="result-card">
                    <h2 style="color: #2E7D32; margin-bottom: 5px;">{plant_part} Report</h2>
                    <h4 style="color: #555;">Detected: <span style="color: #d32f2f;">{disease_part}</span></h4>
                    <hr>
                    <div class="report-text">
                        <p><strong>Analysis:</strong> {report['description']}</p>
                        <p><strong>Recommended Action:</strong> {report['action']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- About Page ---
elif app_mode == "About project":
    st.header("Project Overview")
    st.info("This system is powered by a Deep Convolutional Neural Network (CNN) trained on the PlantVillage dataset.")
    st.write("Current Accuracy: ~96% across 38 specific plant-disease classes.")