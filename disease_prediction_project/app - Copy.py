from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Load dataset with error handling
try:
    # Use raw string or forward slashes for Windows paths
    file_path = r"D:\disease_prediction_project\disease_dataset.csv"
    
    # Alternative: Use forward slashes
    # file_path = "D:/disease_prediction_project/disease_dataset.csv"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")
    
    df = pd.read_csv(file_path)
    
    # Check if required columns exist
    required_columns = ['disease', 'symptoms', 'precautions']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' not found in dataset")
    
    # Handle missing values safely
    df["symptoms"] = df["symptoms"].fillna("").astype(str)
    df["precautions"] = df["precautions"].fillna("No precautions available").astype(str)
    
    print(f"Dataset loaded successfully with {len(df)} records")
    
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Please ensure the dataset file exists at the specified path")
    df = pd.DataFrame()  # Empty DataFrame as fallback
except Exception as e:
    print(f"Error loading dataset: {e}")
    df = pd.DataFrame()  # Empty DataFrame as fallback

def calculate_match_score(user_symptoms, disease_symptoms):
    """
    Calculate the match score between user symptoms and disease symptoms
    """
    if not disease_symptoms or len(disease_symptoms) == 0:
        return 0
    
    if not user_symptoms or len(user_symptoms) == 0:
        return 0
    
    matches = 0
    for user_symptom in user_symptoms:
        # Check for partial matches as well (e.g., "head" matches "headache")
        for disease_symptom in disease_symptoms:
            if user_symptom in disease_symptom or disease_symptom in user_symptom:
                matches += 1
                break
    
    # Calculate score based on percentage of disease symptoms matched
    # You can also use: return matches / len(user_symptoms) for user-centric matching
    return matches / len(disease_symptoms)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        user_input = request.form.get("symptoms", "").lower().strip()
        
        if not user_input:
            return render_template(
                "index.html",
                error="Please enter your symptoms"
            )
        
        # Convert input text -> list
        user_symptoms = [
            s.strip()
            for s in user_input.split(",")
            if s.strip() != ""
        ]
        
        if not user_symptoms:
            return render_template(
                "index.html",
                error="Please enter valid symptoms"
            )
        
        # Check if dataset is loaded
        if df.empty:
            return render_template(
                "index.html",
                error="Dataset not loaded properly. Please check the server logs."
            )
        
        best_disease = None
        best_score = 0
        best_precautions = "No precautions available"
        
        for _, row in df.iterrows():
            # Convert to safe string
            symptoms_value = str(row["symptoms"]).lower()
            
            # Skip empty rows
            if not symptoms_value or symptoms_value == "nan":
                continue
            
            disease_symptoms = [
                s.strip()
                for s in symptoms_value.split(",")
                if s.strip() != ""
            ]
            
            score = calculate_match_score(user_symptoms, disease_symptoms)
            
            if score > best_score:
                best_score = score
                best_disease = row["disease"]
                best_precautions = row["precautions"]
        
        confidence = round(best_score * 100, 2) if best_disease else 0
        
        # If no match found
        if best_score == 0:
            return render_template(
                "index.html",
                symptoms=user_input,
                disease="No matching disease found",
                confidence=0,
                precautions="Please consult a doctor for proper diagnosis",
                message="No exact match found. Showing closest match or general advice."
            )
        
        return render_template(
            "index.html",
            symptoms=user_input,
            disease=best_disease,
            confidence=confidence,
            precautions=best_precautions
        )
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return render_template(
            "index.html",
            error=f"An error occurred during prediction: {str(e)}"
        )

@app.route("/symptoms-list")
def symptoms_list():
    """Optional: Return list of all symptoms in dataset"""
    try:
        if df.empty:
            return {"error": "Dataset not available"}, 500
        
        all_symptoms = set()
        for symptoms in df["symptoms"]:
            if symptoms and symptoms != "nan":
                for s in str(symptoms).split(","):
                    all_symptoms.add(s.strip().lower())
        
        return {"symptoms": sorted(list(all_symptoms))}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)