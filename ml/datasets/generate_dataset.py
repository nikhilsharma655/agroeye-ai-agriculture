"""
Generates realistic synthetic agricultural datasets for AgroEye ML models.

We simulate crop-specific parameter ranges based on well-known agronomic
guidelines (N-P-K requirements, temperature/humidity/rainfall/pH tolerance
bands per crop). Each sample is drawn from a crop's realistic distribution
with added noise, producing a dataset that a classifier/regressor can learn
genuine structure from (not random noise).

Run:
    python ml/datasets/generate_dataset.py
Outputs:
    ml/datasets/crop_recommendation.csv
    ml/datasets/crop_yield.csv
    ml/datasets/disease_risk.csv
"""
import numpy as np
import pandas as pd
import os

RNG = np.random.default_rng(42)
OUT_DIR = os.path.dirname(__file__)

CROP_PROFILES = {
    "rice":       {"N": (80, 12), "P": (45, 8),  "K": (40, 8),  "temp": (25, 3), "humidity": (82, 6),  "ph": (6.2, 0.4), "rainfall": (220, 40), "base_yield": 3.8, "soil": ["clay", "loamy"]},
    "maize":      {"N": (85, 15), "P": (48, 10), "K": (20, 6),  "temp": (24, 4), "humidity": (62, 8),  "ph": (6.3, 0.4), "rainfall": (90, 25),  "base_yield": 4.2, "soil": ["loamy", "sandy"]},
    "chickpea":   {"N": (40, 8),  "P": (65, 10), "K": (80, 10), "temp": (19, 3), "humidity": (16, 5),  "ph": (7.3, 0.4), "rainfall": (65, 15),  "base_yield": 1.6, "soil": ["loamy", "clay"]},
    "kidneybeans":{"N": (20, 6),  "P": (60, 8),  "K": (20, 5),  "temp": (18, 3), "humidity": (21, 5),  "ph": (5.8, 0.3), "rainfall": (95, 20),  "base_yield": 1.4, "soil": ["loamy", "sandy"]},
    "wheat":      {"N": (100,15), "P": (50, 10), "K": (40, 8),  "temp": (18, 4), "humidity": (55, 8),  "ph": (6.8, 0.4), "rainfall": (75, 20),  "base_yield": 3.2, "soil": ["loamy", "clay"]},
    "cotton":     {"N": (120,15), "P": (45, 8),  "K": (55, 8),  "temp": (27, 3), "humidity": (72, 7),  "ph": (6.9, 0.4), "rainfall": (85, 20),  "base_yield": 2.1, "soil": ["black", "sandy"]},
    "sugarcane":  {"N": (140,20), "P": (55, 10), "K": (60, 10), "temp": (28, 3), "humidity": (75, 7),  "ph": (6.5, 0.4), "rainfall": (180, 30), "base_yield": 68.0, "soil": ["loamy", "clay"]},
    "banana":     {"N": (100,15), "P": (75, 10), "K": (200,25), "temp": (27, 2), "humidity": (78, 6),  "ph": (6.0, 0.3), "rainfall": (160, 30), "base_yield": 32.0, "soil": ["loamy", "sandy"]},
    "coffee":     {"N": (100,15), "P": (18, 6),  "K": (30, 8),  "temp": (24, 2), "humidity": (58, 8),  "ph": (6.6, 0.4), "rainfall": (150, 30), "base_yield": 1.1, "soil": ["loamy", "red"]},
    "mango":      {"N": (20, 6),  "P": (27, 6),  "K": (30, 8),  "temp": (30, 3), "humidity": (50, 8),  "ph": (6.0, 0.4), "rainfall": (95, 25),  "base_yield": 8.5, "soil": ["loamy", "red"]},
    "grapes":     {"N": (18, 5),  "P": (130,15), "K": (200,20), "temp": (23, 3), "humidity": (81, 6),  "ph": (6.0, 0.3), "rainfall": (70, 15),  "base_yield": 9.0, "soil": ["sandy", "loamy"]},
    "watermelon": {"N": (99, 12), "P": (17, 5),  "K": (50, 8),  "temp": (25, 3), "humidity": (85, 5),  "ph": (6.5, 0.3), "rainfall": (45, 12),  "base_yield": 18.0, "soil": ["sandy", "loamy"]},
    "lentil":     {"N": (18, 5),  "P": (68, 8),  "K": (19, 5),  "temp": (24, 3), "humidity": (65, 8),  "ph": (6.9, 0.4), "rainfall": (45, 12),  "base_yield": 1.1, "soil": ["loamy", "clay"]},
    "orange":     {"N": (20, 6),  "P": (18, 5),  "K": (10, 4),  "temp": (22, 3), "humidity": (92, 4),  "ph": (7.0, 0.4), "rainfall": (110, 25), "base_yield": 12.0, "soil": ["loamy", "red"]},
    "coconut":    {"N": (22, 6),  "P": (17, 5),  "K": (32, 8),  "temp": (27, 2), "humidity": (94, 3),  "ph": (5.9, 0.3), "rainfall": (170, 30), "base_yield": 6.5, "soil": ["sandy", "loamy"]},
}

SOIL_TYPES = ["loamy", "sandy", "clay", "black", "red"]


def sample_normal(mean_std, low=None, high=None):
    mean, std = mean_std
    val = RNG.normal(mean, std)
    if low is not None:
        val = max(low, val)
    if high is not None:
        val = min(high, val)
    return val


def generate_crop_recommendation(n_per_crop=140):
    rows = []
    for crop, prof in CROP_PROFILES.items():
        for _ in range(n_per_crop):
            n = sample_normal(prof["N"], 0, 200)
            p = sample_normal(prof["P"], 0, 200)
            k = sample_normal(prof["K"], 0, 250)
            temp = sample_normal(prof["temp"], 5, 45)
            hum = sample_normal(prof["humidity"], 10, 100)
            ph = sample_normal(prof["ph"], 3.5, 9.5)
            rain = sample_normal(prof["rainfall"], 10, 300)
            soil = RNG.choice(prof["soil"]) if RNG.random() < 0.8 else RNG.choice(SOIL_TYPES)
            rows.append([n, p, k, temp, hum, ph, rain, soil, crop])
    df = pd.DataFrame(rows, columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "soil_type", "label"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(os.path.join(OUT_DIR, "crop_recommendation.csv"), index=False)
    return df


def generate_yield_dataset(n_per_crop=120):
    rows = []
    for crop, prof in CROP_PROFILES.items():
        for _ in range(n_per_crop):
            area = RNG.uniform(0.5, 20)
            n = sample_normal(prof["N"], 0, 200)
            p = sample_normal(prof["P"], 0, 200)
            k = sample_normal(prof["K"], 0, 250)
            temp = sample_normal(prof["temp"], 5, 45)
            hum = sample_normal(prof["humidity"], 10, 100)
            ph = sample_normal(prof["ph"], 3.5, 9.5)
            rain = sample_normal(prof["rainfall"], 10, 300)

            ideal = prof
            temp_fit = max(0, 1 - abs(temp - ideal["temp"][0]) / (ideal["temp"][0] + 10))
            hum_fit = max(0, 1 - abs(hum - ideal["humidity"][0]) / (ideal["humidity"][0] + 20))
            ph_fit = max(0, 1 - abs(ph - ideal["ph"][0]) / 3.0)
            rain_fit = max(0, 1 - abs(rain - ideal["rainfall"][0]) / (ideal["rainfall"][0] + 50))
            n_fit = max(0, 1 - abs(n - ideal["N"][0]) / (ideal["N"][0] + 50))
            fit = np.clip((temp_fit + hum_fit + ph_fit + rain_fit + n_fit) / 5, 0.15, 1.0)

            yield_per_hectare = ideal["base_yield"] * fit * RNG.normal(1.0, 0.08)
            yield_per_hectare = max(0.05, yield_per_hectare)
            total_yield = yield_per_hectare * area

            rows.append([crop, area, n, p, k, temp, hum, ph, rain, round(yield_per_hectare, 3), round(total_yield, 3)])
    df = pd.DataFrame(rows, columns=["crop", "area_hectare", "N", "P", "K", "temperature", "humidity", "ph",
                                      "rainfall", "yield_per_hectare", "total_yield"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(os.path.join(OUT_DIR, "crop_yield.csv"), index=False)
    return df


def generate_disease_risk_dataset(n=2200):
    rows = []
    growth_stages = ["seedling", "vegetative", "flowering", "maturity"]
    crops = list(CROP_PROFILES.keys())
    for _ in range(n):
        crop = RNG.choice(crops)
        prof = CROP_PROFILES[crop]
        temp = sample_normal(prof["temp"], 5, 45)
        hum = RNG.uniform(20, 100)
        rain = RNG.uniform(0, 300)
        soil_moisture = RNG.uniform(5, 95)
        stage = RNG.choice(growth_stages)
        prev_disease = RNG.choice([0, 1], p=[0.75, 0.25])

        risk_score = (
            0.35 * (hum / 100) +
            0.25 * (min(rain, 200) / 200) +
            0.15 * (1 if 20 <= temp <= 32 else 0.3) +
            0.15 * (soil_moisture / 100) +
            0.10 * prev_disease
        )
        risk_score = np.clip(risk_score + RNG.normal(0, 0.06), 0, 1)

        if risk_score < 0.4:
            level = "low"
            disease = "none_significant"
        elif risk_score < 0.65:
            level = "medium"
            disease = RNG.choice(["leaf_blight", "powdery_mildew", "rust"])
        else:
            level = "high"
            disease = RNG.choice(["blast", "bacterial_wilt", "downy_mildew", "root_rot"])

        rows.append([crop, temp, hum, rain, soil_moisture, stage, prev_disease, round(risk_score * 100, 1), level, disease])
    df = pd.DataFrame(rows, columns=["crop", "temperature", "humidity", "rainfall", "soil_moisture",
                                      "growth_stage", "previous_disease_history", "risk_percentage",
                                      "risk_level", "disease_category"])
    df.to_csv(os.path.join(OUT_DIR, "disease_risk.csv"), index=False)
    return df


if __name__ == "__main__":
    crop_df = generate_crop_recommendation()
    yield_df = generate_yield_dataset()
    disease_df = generate_disease_risk_dataset()
    print(f"crop_recommendation.csv: {crop_df.shape}")
    print(f"crop_yield.csv: {yield_df.shape}")
    print(f"disease_risk.csv: {disease_df.shape}")
