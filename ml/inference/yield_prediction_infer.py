"""
Inference wrapper for the crop yield prediction model.
"""
import os
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saved_models")

_model = joblib.load(os.path.join(MODEL_DIR, "yield_prediction_model.pkl"))
_scaler = joblib.load(os.path.join(MODEL_DIR, "yield_prediction_scaler.pkl"))
_feature_cols = joblib.load(os.path.join(MODEL_DIR, "yield_prediction_features.pkl"))
_crops = joblib.load(os.path.join(MODEL_DIR, "yield_prediction_crops.pkl"))

import json
with open(os.path.join(MODEL_DIR, "yield_prediction_metadata.json")) as f:
    _metadata = json.load(f)
_residual_std = _metadata.get("residual_std", 0.3)


def predict(crop, area_hectare, n, p, k, temperature, humidity, ph, rainfall):
    crop_key = crop.lower().strip()
    row = {"area_hectare": area_hectare, "N": n, "P": p, "K": k,
           "temperature": temperature, "humidity": humidity, "ph": ph, "rainfall": rainfall}
    for c in _crops:
        row[f"crop_{c}"] = 1 if c == crop_key else 0

    known_crop = crop_key in _crops
    X = np.array([[row.get(c, 0) for c in _feature_cols]])
    X_scaled = _scaler.transform(X)

    yield_per_hectare = max(0.0, float(_model.predict(X_scaled)[0]))
    total_yield = yield_per_hectare * area_hectare

    low = max(0.0, yield_per_hectare - 1.28 * _residual_std)
    high = yield_per_hectare + 1.28 * _residual_std

    return {
        "crop": crop,
        "yield_per_hectare": round(yield_per_hectare, 2),
        "estimated_total_yield": round(total_yield, 2),
        "confidence_range_per_hectare": {"low": round(low, 2), "high": round(high, 2)},
        "unit": "tonnes",
        "note": None if known_crop else (
            f"'{crop}' was not in the training crop list; estimate falls back to "
            "environmental features only and may be less reliable."
        ),
    }
