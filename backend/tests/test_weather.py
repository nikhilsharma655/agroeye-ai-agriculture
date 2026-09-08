import pytest
from app.services import weather_service


def test_refresh_weather_no_location(client, auth_headers):
    resp = client.post("/api/farms", json={"name": "No Location Farm", "area": 1.0}, headers=auth_headers)
    farm_id = resp.json()["data"]["id"]

    resp = client.post(f"/api/farms/{farm_id}/weather/refresh", headers=auth_headers)
    assert resp.status_code == 400
    assert resp.json()["error"] == "FARM_LOCATION_MISSING"


def test_refresh_weather_success(client, auth_headers, sample_farm, monkeypatch):
    def fake_get_live_weather(location):
        assert location == sample_farm["location"] or location  # farm has some location
        return {
            "temperature": 28.4, "humidity": 71.0, "rainfall": 2.3,
            "observed_at": "2026-09-05T12:00", "resolved_location": "Test Loc, Test Country",
        }

    monkeypatch.setattr(weather_service, "get_live_weather_for_location", fake_get_live_weather)

    resp = client.post(f"/api/farms/{sample_farm['id']}/weather/refresh", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["temperature"] == 28.4
    assert data["humidity"] == 71.0
    assert data["farm_updated"] is True

    # Confirm the farm's stored readings were actually updated in the DB.
    farm_resp = client.get(f"/api/farms/{sample_farm['id']}", headers=auth_headers)
    farm = farm_resp.json()["data"]
    assert farm["temperature"] == 28.4
    assert farm["humidity"] == 71.0


def test_refresh_weather_service_unavailable(client, auth_headers, sample_farm, monkeypatch):
    def fake_fail(location):
        raise weather_service.WeatherServiceError("Could not reach the weather service. Try again later.")

    monkeypatch.setattr(weather_service, "get_live_weather_for_location", fake_fail)

    resp = client.post(f"/api/farms/{sample_farm['id']}/weather/refresh", headers=auth_headers)
    assert resp.status_code == 502
    assert resp.json()["error"] == "WEATHER_SERVICE_ERROR"


def test_geocode_location_empty_raises():
    with pytest.raises(weather_service.WeatherServiceError):
        weather_service.geocode_location("")
