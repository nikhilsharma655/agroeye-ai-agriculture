"""
Trains and evaluates multiple Scikit-learn classifiers for crop recommendation,
selects the best-performing model based on weighted F1-score, and serializes
the winner (plus label encoder and feature schema) via Joblib.
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from preprocessing.preprocess import CROP_FEATURES, SOIL_TYPES, encode_soil_type  # noqa: E402

DATASET_PATH = os.path.join(BASE_DIR, "datasets", "crop_recommendation.csv")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
EVAL_DIR = os.path.join(os.path.dirname(BASE_DIR), "ml", "evaluation")
os.makedirs(MODEL_DIR, exist_ok=True)


def main():
    df = pd.read_csv(DATASET_PATH)
    df_enc = encode_soil_type(df, "soil_type")

    feature_cols = CROP_FEATURES + [f"soil_{s}" for s in SOIL_TYPES]
    X = df_enc[feature_cols]
    y = df_enc["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    candidates = {
        "random_forest": RandomForestClassifier(n_estimators=300, max_depth=None, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=200, learning_rate=0.08, random_state=42),
        "logistic_regression": LogisticRegression(max_iter=2000),
    }

    results = {}
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, average="weighted", zero_division=0)
        rec = recall_score(y_test, preds, average="weighted", zero_division=0)
        f1 = f1_score(y_test, preds, average="weighted", zero_division=0)
        results[name] = {"accuracy": acc, "precision": prec, "recall": rec, "f1_score": f1}
        fitted[name] = model
        print(f"[{name}] acc={acc:.4f} prec={prec:.4f} rec={rec:.4f} f1={f1:.4f}")

    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best_model = fitted[best_name]
    print(f"\nBest model: {best_name}")

    cm = confusion_matrix(y_test, best_model.predict(X_test_scaled)).tolist()

    joblib.dump(best_model, os.path.join(MODEL_DIR, "crop_recommendation_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "crop_recommendation_scaler.pkl"))
    joblib.dump(sorted(y.unique().tolist()), os.path.join(MODEL_DIR, "crop_recommendation_classes.pkl"))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, "crop_recommendation_features.pkl"))

    metadata = {
        "best_model": best_name,
        "feature_columns": feature_cols,
        "classes": sorted(y.unique().tolist()),
        "metrics": results,
        "confusion_matrix": cm,
    }
    with open(os.path.join(MODEL_DIR, "crop_recommendation_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved model + scaler + metadata to {MODEL_DIR}")


if __name__ == "__main__":
    main()
