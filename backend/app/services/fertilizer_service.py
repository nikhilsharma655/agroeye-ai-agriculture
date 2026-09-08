"""
Fertilizer recommendation logic.

This module uses deterministic agronomic reference values (ideal N-P-K bands
per crop, derived from the same crop profiles used to generate ML training
data) rather than a black-box model, because fertilizer dosing is a
well-understood deficit-correction calculation. It is intentionally kept in
the backend service layer (never in React) and clearly labeled as an
AI-assisted estimate per product requirements.
"""
from typing import Dict, List

# Ideal N-P-K targets per crop (kg/ha), consistent with ml/datasets crop profiles.
CROP_NPK_TARGETS = {
    "rice": {"N": 100, "P": 50, "K": 50},
    "maize": {"N": 120, "P": 60, "K": 40},
    "wheat": {"N": 120, "P": 60, "K": 40},
    "cotton": {"N": 140, "P": 60, "K": 60},
    "sugarcane": {"N": 170, "P": 65, "K": 70},
    "banana": {"N": 200, "P": 90, "K": 250},
    "chickpea": {"N": 25, "P": 60, "K": 30},
    "kidneybeans": {"N": 25, "P": 60, "K": 25},
    "coffee": {"N": 120, "P": 30, "K": 40},
    "mango": {"N": 100, "P": 50, "K": 100},
    "grapes": {"N": 100, "P": 130, "K": 200},
    "watermelon": {"N": 100, "P": 40, "K": 60},
    "lentil": {"N": 20, "P": 70, "K": 20},
    "orange": {"N": 100, "P": 30, "K": 40},
    "coconut": {"N": 50, "P": 30, "K": 100},
}

DEFAULT_TARGET = {"N": 90, "P": 50, "K": 45}

GROWTH_STAGE_MULTIPLIER = {
    "seedling": 0.5,
    "vegetative": 1.0,
    "flowering": 1.15,
    "maturity": 0.4,
}

# Simple fertilizer product mapping per nutrient deficiency
FERTILIZER_SOURCES = {
    "N": "Urea (46% N)",
    "P": "DAP / Single Super Phosphate",
    "K": "Muriate of Potash (MOP)",
}


def recommend_fertilizer(crop: str, nitrogen: float, phosphorus: float, potassium: float,
                          ph: float, soil_type: str = "loamy", growth_stage: str = "vegetative") -> Dict:
    target = CROP_NPK_TARGETS.get(crop.lower().strip(), DEFAULT_TARGET)
    stage_mult = GROWTH_STAGE_MULTIPLIER.get(growth_stage, 1.0)

    deficits = {
        "N": max(0.0, (target["N"] * stage_mult) - nitrogen),
        "P": max(0.0, (target["P"] * stage_mult) - phosphorus),
        "K": max(0.0, (target["K"] * stage_mult) - potassium),
    }

    deficiency_labels = {}
    for nutrient, deficit in deficits.items():
        if deficit <= 5:
            deficiency_labels[nutrient] = "sufficient"
        elif deficit <= 25:
            deficiency_labels[nutrient] = "mildly deficient"
        else:
            deficiency_labels[nutrient] = "significantly deficient"

    recommended_products: List[str] = [
        FERTILIZER_SOURCES[n] for n, d in deficits.items() if d > 5
    ]
    if not recommended_products:
        recommended_products = ["No additional fertilizer needed at this time"]

    # pH-based amendment
    ph_note = ""
    if ph < 5.5:
        ph_note = " Soil is acidic — consider agricultural lime to raise pH before heavy fertilization."
    elif ph > 7.8:
        ph_note = " Soil is alkaline — consider elemental sulfur or organic matter to lower pH."

    reason = (
        f"Target N-P-K for {crop} at the {growth_stage} stage is approximately "
        f"N={round(target['N'] * stage_mult)}, P={round(target['P'] * stage_mult)}, "
        f"K={round(target['K'] * stage_mult)} kg/ha. Current soil levels are N={nitrogen}, "
        f"P={phosphorus}, K={potassium}." + ph_note
    )

    return {
        "recommended_fertilizer": recommended_products,
        "approximate_quantity_kg_per_hectare": {k: round(v, 1) for k, v in deficits.items()},
        "nutrient_deficiency": deficiency_labels,
        "reason": reason,
    }
