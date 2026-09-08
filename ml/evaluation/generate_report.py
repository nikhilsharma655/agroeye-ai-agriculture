"""
Reads the metadata JSON files produced by training scripts and prints/saves a
consolidated evaluation report (also used to sanity-check models before
deploying them behind the FastAPI service layer).
"""
import json
import os

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saved_models")
REPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_report.md")


def main():
    lines = ["# AgroEye ML Evaluation Report\n"]
    for fname, title in [
        ("crop_recommendation_metadata.json", "Crop Recommendation (Classification)"),
        ("yield_prediction_metadata.json", "Yield Prediction (Regression)"),
        ("disease_risk_metadata.json", "Disease Risk (Classification)"),
    ]:
        path = os.path.join(MODEL_DIR, fname)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            meta = json.load(f)
        lines.append(f"\n## {title}\n")
        lines.append(f"**Selected model:** `{meta['best_model']}`\n")
        lines.append("\n| Model | Metrics |\n|---|---|")
        for name, metrics in meta["metrics"].items():
            metrics_str = ", ".join(f"{k}={v:.4f}" for k, v in metrics.items())
            lines.append(f"| {name} | {metrics_str} |")
    report = "\n".join(lines)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
