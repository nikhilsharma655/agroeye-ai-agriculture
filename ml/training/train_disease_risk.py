"""
Trains a Scikit-learn classifier for structured-data disease risk-level
prediction (low/medium/high). Designed so an image-based CNN model can later
be added as an alternate inference path without touching this pipeline.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "disease_risk.csv")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

GROWTH_STAGES = ["seedling", "vegetative", "flowering", "maturity"]
CROPS = ["rice", "maize", "chickpea", "kidneybeans", "wheat", "cotton", "sugarcane",
         "banana", "coffee", "mango", "grapes", "watermelon", "lentil", "orange", "coconut"]


def main():
    df = pd.read_csv(DATASET_PATH)

    for stage in GROWTH_STAGES:
        df[f"stage_{stage}"] = (df["growth_stage"] == stage).astype(int)
    for crop in CROPS:
        df[f"crop_{crop}"] = (df["crop"] == crop).astype(int)

    feature_cols = (["temperature", "humidity", "rainfall", "soil_moisture", "previous_disease_history"]
                     + [f"stage_{s}" for s in GROWTH_STAGES]
                     + [f"crop_{c}" for c in CROPS])

    X = df[feature_cols]
    le = LabelEncoder()
    y = le.fit_transform(df["risk_level"])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    candidates = {
        "random_forest": RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=200, random_state=42),
    }

    results, fitted = {}, {}
    for name, model in candidates.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        results[name] = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, average="weighted", zero_division=0),
            "recall": recall_score(y_test, preds, average="weighted", zero_division=0),
            "f1_score": f1_score(y_test, preds, average="weighted", zero_division=0),
        }
        fitted[name] = model
        print(f"[{name}] {results[name]}")

    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best_model = fitted[best_name]
    cm = confusion_matrix(y_test, best_model.predict(X_test_scaled)).tolist()
    print(f"\nBest model: {best_name}")

    joblib.dump(best_model, os.path.join(MODEL_DIR, "disease_risk_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "disease_risk_scaler.pkl"))
    joblib.dump(le, os.path.join(MODEL_DIR, "disease_risk_label_encoder.pkl"))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, "disease_risk_features.pkl"))

    metadata = {
        "best_model": best_name,
        "feature_columns": feature_cols,
        "classes": le.classes_.tolist(),
        "metrics": results,
        "confusion_matrix": cm,
    }
    with open(os.path.join(MODEL_DIR, "disease_risk_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nSaved model + scaler + metadata to {MODEL_DIR}")


if __name__ == "__main__":
    main()
