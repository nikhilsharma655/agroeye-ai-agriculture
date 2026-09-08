"""
Irrigation recommendation logic — implemented entirely in the backend
(never hardcoded in React) as required by the product spec.

Uses a water-balance-style heuristic: soil moisture deficit vs. crop-specific
target moisture, adjusted by temperature (evapotranspiration proxy), rainfall
(recent supply), humidity, and growth stage (water sensitivity), to estimate
a litres-per-farm irrigation requirement.
"""
from typing import Dict

CROP_TARGET_MOISTURE = {
    "rice": 80, "maize": 55, "wheat": 50, "cotton": 55, "sugarcane": 65,
    "banana": 70, "chickpea": 35, "kidneybeans": 45, "coffee": 60, "mango": 45,
    "grapes": 50, "watermelon": 65, "lentil": 40, "orange": 55, "coconut": 70,
}
DEFAULT_TARGET_MOISTURE = 55

GROWTH_STAGE_WATER_SENSITIVITY = {
    "seedling": 1.1,
    "vegetative": 1.0,
    "flowering": 1.25,   # most water-sensitive stage for most crops
    "maturity": 0.6,
}

# Litres of water per hectare per 1% moisture deficit (rough agronomic rule of thumb)
LITRES_PER_HECTARE_PER_PERCENT_DEFICIT = 250


def recommend_irrigation(crop: str, soil_moisture: float, temperature: float, humidity: float,
                          rainfall: float, area_hectare: float, growth_stage: str = "vegetative") -> Dict:
    target_moisture = CROP_TARGET_MOISTURE.get(crop.lower().strip(), DEFAULT_TARGET_MOISTURE)
    sensitivity = GROWTH_STAGE_WATER_SENSITIVITY.get(growth_stage, 1.0)

    deficit = max(0.0, target_moisture - soil_moisture)

    # Heat increases evapotranspiration; recent rainfall reduces net need; low humidity increases need
    temp_factor = 1.0 + max(0.0, (temperature - 25) * 0.02)
    humidity_factor = 1.0 + max(0.0, (60 - humidity) * 0.005)
    rainfall_offset_pct = min(deficit, rainfall / 10.0)  # 10mm rainfall ~ offsets 1% moisture deficit, capped

    effective_deficit = max(0.0, (deficit - rainfall_offset_pct) * sensitivity * temp_factor * humidity_factor)

    if effective_deficit <= 3:
        water_status = "Adequate"
        irrigation_required = False
        level = "None"
    elif effective_deficit <= 12:
        water_status = "Moderate"
        irrigation_required = True
        level = "Light"
    elif effective_deficit <= 25:
        water_status = "Low"
        irrigation_required = True
        level = "Moderate"
    else:
        water_status = "Critical"
        irrigation_required = True
        level = "Heavy"

    litres_center = effective_deficit * LITRES_PER_HECTARE_PER_PERCENT_DEFICIT * area_hectare
    litres_low = max(0.0, litres_center * 0.85)
    litres_high = litres_center * 1.15

    reason = (
        f"Soil moisture is {soil_moisture}% vs a target of ~{target_moisture}% for {crop} "
        f"at the {growth_stage} stage. Temperature ({temperature}°C) and humidity ({humidity}%) "
        f"increase evapotranspiration; recent rainfall ({rainfall}mm) partially offsets the deficit."
    )

    return {
        "irrigation_required": irrigation_required,
        "water_status": water_status,
        "recommended_level": level,
        "estimated_requirement_litres": {"low": round(litres_low), "high": round(litres_high)},
        "reason": reason,
    }
