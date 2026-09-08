"""
Trains and evaluates Scikit-learn regressors for crop yield prediction,
selects the best-performing model based on R^2 score, and serializes it.
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "crop_yield.csv")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

CROP_LIST = None  # filled at runtime from data


def main():
    df = pd.read_csv(DATASET_PATH)
    crops = sorted(df["crop"].unique().tolist())
    crop_dummies = pd.get_dummies(df["crop"], prefix="crop")
    for c in crops:
        col = f"crop_{c}"
        if col not in crop_dummies.columns:
            crop_dummies[col] = 0
    crop_cols = [f"crop_{c}" for c in crops]
    crop_dummies = crop_dummies[crop_cols]

    numeric_cols = ["area_hectare", "N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    X = pd.concat([df[numeric_cols], crop_dummies], axis=1)
    y = df["yield_per_hectare"]

    feature_cols = numeric_cols + crop_cols

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    candidates = {
        "random_forest": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(n_estimators=250, learning_rate=0.06, random_state=42),
        "linear_regression": LinearRegression(),
    }

    results = {}
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, preds)
        mse = mean_squared_error(y_test, preds)
        rmse = float(np.sqrt(mse))
        r2 = r2_score(y_test, preds)
        results[name] = {"mae": mae, "mse": mse, "rmse": rmse, "r2": r2}
        fitted[name] = model
        print(f"[{name}] MAE={mae:.4f} MSE={mse:.4f} RMSE={rmse:.4f} R2={r2:.4f}")

    best_name = max(results, key=lambda k: results[k]["r2"])
    best_model = fitted[best_name]
    print(f"\nBest model: {best_name}")

    # residual std per crop-agnostic model, used to build a confidence range at inference time
    residuals = y_test.values - best_model.predict(X_test_scaled)
    residual_std = float(np.std(residuals))

    joblib.dump(best_model, os.path.join(MODEL_DIR, "yield_prediction_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "yield_prediction_scaler.pkl"))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, "yield_prediction_features.pkl"))
    joblib.dump(crops, os.path.join(MODEL_DIR, "yield_prediction_crops.pkl"))

    metadata = {
        "best_model": best_name,
        "feature_columns": feature_cols,
        "crops": crops,
        "metrics": results,
        "residual_std": residual_std,
    }
    with open(os.path.join(MODEL_DIR, "yield_prediction_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved model + scaler + metadata to {MODEL_DIR}")


if __name__ == "__main__":
    main()
