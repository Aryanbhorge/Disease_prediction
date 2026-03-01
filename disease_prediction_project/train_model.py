import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# --- SAMPLE DATASET (You can replace later) ---

data = pd.DataFrame({
    "symptom1": [1, 2, 3, 4, 5, 6],
    "symptom2": [2, 3, 4, 5, 6, 7],
    "risk_score": [3, 4, 5, 6, 7, 8]
})

X = data[["symptom1", "symptom2"]]
y = data["risk_score"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model file
pickle.dump(model, open("model.pkl", "wb"))

print("Model trained & saved as model.pkl")
