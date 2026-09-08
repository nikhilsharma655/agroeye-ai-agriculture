"""
Inference wrapper for the crop recommendation model.
Loads serialized artifacts once (module import time) and exposes a pure
`predict()` function consumed by the FastAPI service layer.
"""
import os
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saved_models")

_model = joblib.load(os.path.join(MODEL_DIR, "crop_recommendation_model.pkl"))
_scaler = joblib.load(os.path.join(MODEL_DIR, "crop_recommendation_scaler.pkl"))
_classes = joblib.load(os.path.join(MODEL_DIR, "crop_recommendation_classes.pkl"))
_feature_cols = joblib.load(os.path.join(MODEL_DIR, "crop_recommendation_features.pkl"))

SOIL_TYPES = ["loamy", "sandy", "clay", "black", "red"]


def _build_feature_vector(n, p, k, temperature, humidity, ph, rainfall, soil_type):
    row = {"N": n, "P": p, "K": k, "temperature": temperature, "humidity": humidity,
           "ph": ph, "rainfall": rainfall}
    for soil in SOIL_TYPES:
        row[f"soil_{soil}"] = 1 if soil_type == soil else 0
    return np.array([[row[c] for c in _feature_cols]])


def predict(n, p, k, temperature, humidity, ph, rainfall, soil_type="loamy", top_k=5):
    """Returns the top-k recommended crops with probability scores."""
    X = _build_feature_vector(n, p, k, temperature, humidity, ph, rainfall, soil_type)
    X_scaled = _scaler.transform(X)

    if hasattr(_model, "predict_proba"):
        probs = _model.predict_proba(X_scaled)[0]
        model_classes = _model.classes_
    else:
        pred = _model.predict(X_scaled)[0]
        probs = np.array([1.0 if c == pred else 0.0 for c in _classes])
        model_classes = np.array(_classes)

    order = np.argsort(probs)[::-1][:top_k]
    ranked = [
        {"crop": str(model_classes[i]), "confidence": round(float(probs[i]) * 100, 2)}
        for i in order
    ]
    best = ranked[0]

    explanation = (
        f"Based on N={n}, P={p}, K={k}, pH={ph}, temperature={temperature}°C, "
        f"humidity={humidity}%, and rainfall={rainfall}mm, '{best['crop']}' matches the "
        f"learned soil-and-climate profile most closely among {len(model_classes)} crops."
    )

    return {
        "recommended_crop": best["crop"],
        "suitability_score": best["confidence"],
        "top_recommendations": ranked,
        "explanation": explanation,
    }
