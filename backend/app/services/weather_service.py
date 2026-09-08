"""
Live weather integration via Open-Meteo (https://open-meteo.com) — chosen
specifically because it requires no API key/signup, keeping this project
fully self-contained. If a farm has no resolvable location, or the API is
unreachable, callers get a clear structured error rather than a crash, and
existing manually-entered farm readings remain untouched.

Two calls are made:
1. Geocoding API — resolves a free-text location string (e.g. "Ludhiana,
   Punjab") into latitude/longitude.
2. Forecast API — fetches current temperature, humidity, and precipitation
   for those coordinates.
"""
import logging
import httpx
from typing import Optional, Dict

logger = logging.getLogger("agroeye.weather")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT = 6.0


class WeatherServiceError(Exception):
    """Raised when live weather data cannot be retrieved for a location."""


def geocode_location(location: str) -> Dict:
    """Resolves a free-text location to coordinates. Raises WeatherServiceError
    if the location is empty, unresolvable, or the geocoding service fails."""
    if not location or not location.strip():
        raise WeatherServiceError("Farm has no location set; cannot look up weather.")

    try:
        response = httpx.get(GEOCODING_URL, params={"name": location, "count": 1}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        logger.warning("Geocoding request failed for '%s': %s", location, exc)
        raise WeatherServiceError("Could not reach the geocoding service. Try again later.") from exc

    results = data.get("results") or []
    if not results:
        raise WeatherServiceError(f"Could not resolve location '{location}' to coordinates.")

    top = results[0]
    return {
        "latitude": top["latitude"],
        "longitude": top["longitude"],
        "resolved_name": ", ".join(filter(None, [top.get("name"), top.get("admin1"), top.get("country")])),
    }


def fetch_current_weather(latitude: float, longitude: float) -> Dict:
    """Fetches current temperature (°C), relative humidity (%), and the last
    hour's precipitation (mm, used as a rainfall proxy) for the given
    coordinates. Raises WeatherServiceError on failure."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "auto",
    }
    try:
        response = httpx.get(FORECAST_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        logger.warning("Forecast request failed for (%s, %s): %s", latitude, longitude, exc)
        raise WeatherServiceError("Could not reach the weather service. Try again later.") from exc

    current = data.get("current")
    if not current:
        raise WeatherServiceError("Weather service returned no current conditions for this location.")

    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "rainfall": current.get("precipitation", 0.0),
        "observed_at": current.get("time"),
    }


def get_live_weather_for_location(location: str) -> Dict:
    """Convenience wrapper: geocode then fetch in one call. Returns a dict
    with temperature, humidity, rainfall, observed_at, and resolved_location."""
    geo = geocode_location(location)
    weather = fetch_current_weather(geo["latitude"], geo["longitude"])
    weather["resolved_location"] = geo["resolved_name"]
    weather["latitude"] = geo["latitude"]
    weather["longitude"] = geo["longitude"]
    return weather
