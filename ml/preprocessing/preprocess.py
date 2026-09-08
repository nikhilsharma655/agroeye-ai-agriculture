"""
Shared preprocessing utilities for AgroEye ML pipelines.
"""
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

CROP_FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
SOIL_TYPES = ["loamy", "sandy", "clay", "black", "red"]


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def encode_soil_type(df: pd.DataFrame, column: str = "soil_type") -> pd.DataFrame:
    """One-hot encode soil type into fixed known categories so inference-time
    encoding always matches training-time columns."""
    df = df.copy()
    for soil in SOIL_TYPES:
        df[f"soil_{soil}"] = (df[column] == soil).astype(int)
    return df.drop(columns=[column])


def build_label_encoder(labels: pd.Series) -> LabelEncoder:
    le = LabelEncoder()
    le.fit(labels)
    return le


def build_scaler(df: pd.DataFrame) -> StandardScaler:
    scaler = StandardScaler()
    scaler.fit(df)
    return scaler
