from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load dataset safely
df = pd.read_csv(r"D:\disease_prediction_project\disease_dataset.csv", dtype=str)

df["symptoms"] = df["symptoms"].fillna("")
df["precautions"] = df["precautions"].fillna("No precautions available")


# -----------------------------
# Build unique symptom list for auto-suggest
# -----------------------------
all_symptoms = []

for s in df["symptoms"]:
    if isinstance(s, str):
        for item in s.split(","):
            item = item.strip().lower()
            if item and item not in all_symptoms:
                all_symptoms.append(item)

all_symptoms = sorted(all_symptoms)


# -----------------------------
# Score match between symptoms
# -----------------------------
def calculate_match_score(user_symptoms, disease_symptoms):
    if len(disease_symptoms) == 0:
        return 0

    matches = sum(1 for s in user_symptoms if s in disease_symptoms)
    return matches / len(disease_symptoms)


@app.route("/")
def home():
    return render_template(
        "index.html",
        symptoms="",
        symptom_list=all_symptoms
    )


@app.route("/predict", methods=["POST"])
def predict():

    user_input = request.form["symptoms"].lower().strip()

    user_symptoms = [
        s.strip()
        for s in user_input.split(",")
        if s.strip() != ""
    ]

    best_disease = "No matching disease found"
    best_score = 0
    best_precautions = "Please enter more symptoms"

    for _, row in df.iterrows():

        symptoms_value = str(row["symptoms"]).lower()

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

    confidence = 0 if best_score == 0 else round(best_score * 100, 2)

    return render_template(
        "index.html",
        symptoms=user_input,
        disease=best_disease,
        confidence=confidence,
        precautions=best_precautions,
        symptom_list=all_symptoms
    )


if __name__ == "__main__":
    app.run(debug=True)
