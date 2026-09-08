"""
Master training script for all AgroEye ML models.
Run: python ml/training/train_models.py
Generates all serialized artifacts under ml/saved_models/.
"""
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_SCRIPT = os.path.join(os.path.dirname(BASE_DIR), "datasets", "generate_dataset.py")

SCRIPTS = [
    DATASETS_SCRIPT,
    os.path.join(BASE_DIR, "train_crop_recommendation.py"),
    os.path.join(BASE_DIR, "train_yield_prediction.py"),
    os.path.join(BASE_DIR, "train_disease_risk.py"),
]


def main():
    for script in SCRIPTS:
        print(f"\n{'=' * 70}\nRunning: {script}\n{'=' * 70}")
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"FAILED: {script}")
            sys.exit(1)
    print("\nAll models trained and saved successfully.")


if __name__ == "__main__":
    main()
