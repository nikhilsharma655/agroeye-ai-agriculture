"""
Thin service layer bridging FastAPI routes to the ml/ package's inference
modules. Keeps ML logic fully out of route handlers, and means the ml/
package has zero FastAPI/Pydantic dependency of its own.
"""
import sys
import os

ML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml"))
if ML_DIR not in sys.path:
    sys.path.insert(0, ML_DIR)

from inference import crop_recommendation_infer, yield_prediction_infer, disease_risk_infer, disease_image_infer  # noqa: E402


def recommend_crop(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, soil_type="loamy"):
    return crop_recommendation_infer.predict(
        n=nitrogen, p=phosphorus, k=potassium, temperature=temperature,
        humidity=humidity, ph=ph, rainfall=rainfall, soil_type=soil_type,
    )


def predict_yield(crop, area_hectare, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    return yield_prediction_infer.predict(
        crop=crop, area_hectare=area_hectare, n=nitrogen, p=phosphorus, k=potassium,
        temperature=temperature, humidity=humidity, ph=ph, rainfall=rainfall,
    )


def predict_disease_risk(crop, temperature, humidity, rainfall, soil_moisture,
                          growth_stage="vegetative", previous_disease_history=False):
    return disease_risk_infer.predict(
        crop=crop, temperature=temperature, humidity=humidity, rainfall=rainfall,
        soil_moisture=soil_moisture, growth_stage=growth_stage,
        previous_disease_history=previous_disease_history,
    )


def predict_disease_from_image(image_bytes, crop=None):
    """Bridges to the image-based disease detection scaffold. Currently
    raises disease_image_infer.DiseaseImageModelNotAvailable until a real
    image model is trained — see that module's docstring for how to complete
    it. Kept as a separate entry point so wiring it up never touches the
    structured-data disease_risk route/model above."""
    return disease_image_infer.predict_from_image(image_bytes, crop=crop)
