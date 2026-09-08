"""
Aggregates farm data + the other AI services into a consistent list of
farmer-friendly insights (soil, crop, irrigation, yield, disease, fertilizer),
as required by the /api/farms/{id}/insights endpoint.
"""
from typing import List, Dict
from app.services import fertilizer_service, irrigation_service, ml_service


def _severity_from_risk(risk_level: str) -> str:
    return {"low": "low", "medium": "medium", "high": "high"}.get(risk_level, "info")


def generate_insights(farm) -> List[Dict]:
    insights: List[Dict] = []

    crop = farm.current_crop or "rice"
    n = farm.nitrogen if farm.nitrogen is not None else 60
    p = farm.phosphorus if farm.phosphorus is not None else 40
    k = farm.potassium if farm.potassium is not None else 40
    ph = farm.soil_ph if farm.soil_ph is not None else 6.5
    moisture = farm.moisture if farm.moisture is not None else 50
    temp = farm.temperature if farm.temperature is not None else 27
    humidity = farm.humidity if farm.humidity is not None else 60
    rainfall = 80.0  # placeholder default when no weather record is linked yet
    area = farm.area or 1.0

    # --- Soil insight ---
    if n < 40:
        insights.append({
            "category": "soil", "severity": "medium",
            "title": "Low nitrogen levels detected",
            "explanation": f"Your soil nitrogen ({n} kg/ha) is below the healthy range for most crops.",
            "recommended_action": "Consider applying a nitrogen-rich fertilizer such as Urea.",
        })
    else:
        insights.append({
            "category": "soil", "severity": "info",
            "title": "Soil nitrogen is within a healthy range",
            "explanation": f"Nitrogen level of {n} kg/ha is adequate for most crop types.",
            "recommended_action": "Maintain current fertilization schedule.",
        })

    # --- Crop suitability insight ---
    try:
        rec = ml_service.recommend_crop(n, p, k, temp, humidity, ph, rainfall, farm.soil_type or "loamy")
        insights.append({
            "category": "crop", "severity": "info",
            "title": f"{rec['recommended_crop'].title()} appears highly suitable",
            "explanation": rec["explanation"],
            "recommended_action": f"Consider {rec['recommended_crop']} if you are planning your next planting cycle.",
        })
    except Exception:
        pass

    # --- Irrigation insight ---
    irrigation = irrigation_service.recommend_irrigation(crop, moisture, temp, humidity, rainfall, area)
    insights.append({
        "category": "irrigation",
        "severity": "high" if irrigation["water_status"] == "Critical" else (
            "medium" if irrigation["irrigation_required"] else "info"),
        "title": f"Water status: {irrigation['water_status']}",
        "explanation": irrigation["reason"],
        "recommended_action": (
            f"Irrigate at a '{irrigation['recommended_level']}' level "
            f"(~{irrigation['estimated_requirement_litres']['low']}–"
            f"{irrigation['estimated_requirement_litres']['high']} litres)."
            if irrigation["irrigation_required"] else "No irrigation needed right now."
        ),
    })

    # --- Yield insight ---
    try:
        yield_pred = ml_service.predict_yield(crop, area, n, p, k, temp, humidity, ph, rainfall)
        insights.append({
            "category": "yield", "severity": "info",
            "title": f"Estimated yield: {yield_pred['yield_per_hectare']} t/ha",
            "explanation": f"Based on current conditions, {crop} is projected to yield around "
                            f"{yield_pred['yield_per_hectare']} tonnes/hectare "
                            f"({yield_pred['estimated_total_yield']} tonnes total on {area} ha).",
            "recommended_action": "Track actual harvest yield to help refine future predictions.",
        })
    except Exception:
        pass

    # --- Disease insight ---
    try:
        disease = ml_service.predict_disease_risk(crop, temp, humidity, rainfall, moisture)
        insights.append({
            "category": "disease",
            "severity": _severity_from_risk(disease["risk_level"]),
            "title": f"Disease risk: {disease['risk_level'].title()} ({disease['risk_percentage']}%)",
            "explanation": f"Possible concern: {disease['possible_disease_category']}.",
            "recommended_action": disease["preventive_suggestions"][0] if disease["preventive_suggestions"] else "Continue monitoring.",
        })
    except Exception:
        pass

    # --- Fertilizer insight ---
    fert = fertilizer_service.recommend_fertilizer(crop, n, p, k, ph, farm.soil_type or "loamy")
    deficient_nutrients = [k_ for k_, v in fert["nutrient_deficiency"].items() if v != "sufficient"]
    insights.append({
        "category": "fertilizer",
        "severity": "medium" if deficient_nutrients else "info",
        "title": "Fertilizer plan" if deficient_nutrients else "Nutrient levels look sufficient",
        "explanation": fert["reason"],
        "recommended_action": ", ".join(fert["recommended_fertilizer"]),
    })

    return insights
