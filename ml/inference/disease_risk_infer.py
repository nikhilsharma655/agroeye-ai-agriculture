"""
Inference wrapper for structured-data disease risk prediction.
Kept behind a stable predict() interface so an image-based CNN model can
later be swapped/added (e.g. disease_risk_infer.predict_from_image()) without
changing the FastAPI route or service layer contracts.
"""
import os
import json
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saved_models")

_model = joblib.load(os.path.join(MODEL_DIR, "disease_risk_model.pkl"))
_scaler = joblib.load(os.path.join(MODEL_DIR, "disease_risk_scaler.pkl"))
_label_encoder = joblib.load(os.path.join(MODEL_DIR, "disease_risk_label_encoder.pkl"))
_feature_cols = joblib.load(os.path.join(MODEL_DIR, "disease_risk_features.pkl"))

GROWTH_STAGES = ["seedling", "vegetative", "flowering", "maturity"]
CROPS = ["rice", "maize", "chickpea", "kidneybeans", "wheat", "cotton", "sugarcane",
         "banana", "coffee", "mango", "grapes", "watermelon", "lentil", "orange", "coconut"]

PREVENTIVE_TIPS = {
    "low": [
        "Continue routine field monitoring on a weekly basis.",
        "Maintain balanced fertilization to keep plants naturally resilient.",
    ],
    "medium": [
        "Increase field scouting frequency to 2-3 times per week.",
        "Improve drainage/airflow if humidity around the canopy is high.",
        "Consider a preventive bio-fungicide application after consulting a local agronomist.",
    ],
    "high": [
        "Inspect crop immediately for visible lesions, wilting, or discoloration.",
        "Isolate/remove visibly infected plants where feasible to limit spread.",
        "Consult a local agricultural extension officer before applying chemical treatment.",
        "Reduce leaf wetness duration by adjusting irrigation timing (avoid evening watering).",
    ],
}

DISEASE_LABELS = {
    "none_significant": "No significant disease pattern detected",
    "leaf_blight": "Leaf Blight (fungal)",
    "powdery_mildew": "Powdery Mildew (fungal)",
    "rust": "Rust (fungal)",
    "blast": "Blast Disease (fungal)",
    "bacterial_wilt": "Bacterial Wilt",
    "downy_mildew": "Downy Mildew (fungal)",
    "root_rot": "Root Rot (fungal/oomycete)",
}


def predict(crop, temperature, humidity, rainfall, soil_moisture, growth_stage="vegetative",
            previous_disease_history=False):
    row = {
        "temperature": temperature, "humidity": humidity, "rainfall": rainfall,
        "soil_moisture": soil_moisture, "previous_disease_history": int(bool(previous_disease_history)),
    }
    for stage in GROWTH_STAGES:
        row[f"stage_{stage}"] = 1 if growth_stage == stage else 0
    for c in CROPS:
        row[f"crop_{c}"] = 1 if crop.lower().strip() == c else 0

    X = np.array([[row.get(c, 0) for c in _feature_cols]])
    X_scaled = _scaler.transform(X)

    probs = _model.predict_proba(X_scaled)[0]
    pred_idx = int(np.argmax(probs))
    risk_level = _label_encoder.inverse_transform([pred_idx])[0]
    risk_pct = round(float(probs[pred_idx]) * 100, 1)

    # Heuristic disease-category guess conditioned on risk level (kept separate
    # from the ML risk-level classifier; can be replaced by a dedicated
    # multi-label model or an image classifier later).
    if risk_level == "low":
        possible_disease = "none_significant"
    elif risk_level == "medium":
        possible_disease = "leaf_blight" if humidity > 60 else "powdery_mildew"
    else:
        possible_disease = "blast" if rainfall > 150 else "bacterial_wilt"

    return {
        "risk_level": risk_level,
        "risk_percentage": risk_pct,
        "possible_disease_category": DISEASE_LABELS.get(possible_disease, possible_disease),
        "preventive_suggestions": PREVENTIVE_TIPS.get(risk_level, []),
        "class_probabilities": {
            cls: round(float(p) * 100, 1) for cls, p in zip(_label_encoder.classes_, probs)
        },
    }
