from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
import os
import webbrowser
from threading import Timer

# Set template_folder to '.' so it looks for index.html in the same directory
app = Flask(__name__, template_folder='.')

# --- Load Model ---
try:
    model = tf.keras.models.load_model('trained_model.h5')
except Exception as e:
    print(f"Error loading model: {e}")

# --- Full 38 Disease Classes ---
CLASS_NAMES = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy', 
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot', 
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy', 
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 
    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy', 
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy', 
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 
    'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

# --- Clinical Knowledge Base ---
# This covers the specific biology of your dataset's classes
DISEASE_REPORTS = {
    "Healthy": "Specimen exhibits optimal cellular structure and chlorophyll density. No pathogenic intervention required.",
    "Scab": "Detected Venturia inaequalis fungal signatures. Symptoms include olive-green spots turning into corky brown lesions. Recommend localized fungicide and removal of fallen leaf litter.",
    "Rot": "Pathogenic decay detected. Usually indicates Diplodia or Botryosphaeria infection. Symptoms include darkened, sunken necrotic tissue. Pruning and improved drainage are mandatory.",
    "Rust": "Fungal pathogen Gymnosporangium identified. Characteristic orange/yellow spore pustules compromise photosynthetic capability. Requires immediate copper-based treatment.",
    "Mildew": "Erysiphales fungal spores detected. White filamentous growth on the adaxial surface. Increase air circulation and reduce ambient humidity.",
    "Blight": "Aggressive tissue necrosis detected (Phytophthora/Alternaria). Rapidly spreading pathogen causing water-soaked lesions. Immediate isolation of the specimen is critical.",
    "Bacterial Spot": "Xanthomonas signatures present. Small, water-soaked lesions leading to chlorosis. Avoid overhead irrigation and apply bactericide.",
    "Gray Leaf Spot": "Cercospora zeae-maydis detected. Rectangular lesions running parallel to leaf veins. Common in high-moisture environments.",
    "Esca": "Complex fungal vascular disease (Black Measles). Identified by 'tiger-stripe' chlorosis. Requires deep-tissue pruning and vineyard sanitation.",
    "Leaf Blight": "Isariopsis fungal infection. Irregular reddish-brown lesions. Common in dense canopies with poor ventilation.",
    "Citrus Greening": "Candidatus Liberibacter asiaticus (HLB) detected. Systemic bacterial infection causing blotchy mottling and nutrient deficiency. Monitor for psyllid vectors.",
    "Leaf Scorch": "Diplocarpon earlianum identified. Purple/brown spots that coalesce, causing the leaf to appear 'scorched'. Prune affected area.",
    "Leaf Mold": "Passalora fulva signatures. Pale green/yellow spots with velvet-like fungal growth on the underside. Lower greenhouse humidity.",
    "Septoria": "Septoria lycopersici fungal spots. Small circular lesions with gray centers and dark borders. Spreads via splashing water.",
    "Spider Mites": "Arachnid infestation detected (Tetranychus urticae). Results in fine stippling (yellow dots) and webbing. Recommend miticides or predatory insects.",
    "Target Spot": "Corynespora cassiicola identified. Concentric rings within necrotic lesions, resembling a target. Often thrives in warm, humid conditions.",
    "Yellow Leaf Curl": "Begomovirus (TYLCV) signatures. Upward curling of leaves and severe stunting. Vector control (whitefly) is essential.",
    "Mosaic Virus": "Viral pathogenic signature (ToMV). Mottling and 'mosaic' patterns on foliage. Highly stable virus; sanitize all equipment immediately."
}

def generate_report(disease_label):
    # Default message if no specific keyword matches
    report = "Cellular degradation detected. Suggesting clinical isolation, removal of infected foliage, and a broad-spectrum anti-pathogen application."
    
    # Check for 'healthy' first
    if "healthy" in disease_label.lower():
        return DISEASE_REPORTS["Healthy"]
    
    # Match the diagnosis to our knowledge base
    for key, description in DISEASE_REPORTS.items():
        if key.lower() in disease_label.lower():
            report = description
            break
            
    return report

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'})

    # Save temp file for prediction
    temp_path = "temp_analysis.jpg"
    file.save(temp_path)

    try:
        # Image Processing (Matching the 128x128 your model expects)
        image = tf.keras.preprocessing.image.load_img(temp_path, target_size=(128, 128))
        input_arr = tf.keras.preprocessing.image.img_to_array(image)
        input_arr = np.expand_dims(input_arr, axis=0) # Convert to batch
        
        # Run AI Inference
        predictions = model.predict(input_arr)
        result_index = np.argmax(predictions)
        
        # Parse the 'computery' raw name
        raw_name = CLASS_NAMES[result_index]
        parts = raw_name.split('___')
        plant_name = parts[0].replace('_', ' ').title()
        disease_name = parts[1].replace('_', ' ').title()
        
        # Get the professional diagnostic text
        clinical_report = generate_report(disease_name)
        
        # Return the clean JSON
        return jsonify({
            'plant': plant_name,
            'disease': disease_name,
            'report': clinical_report,
            'status': 'Optimal Health' if 'Healthy' in disease_name else 'Action Required'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    # This waits 1.5 seconds, then opens the browser tab automatically
    Timer(1.5, open_browser).start()
    
    # Run the app
    app.run(debug=False, port=5000)