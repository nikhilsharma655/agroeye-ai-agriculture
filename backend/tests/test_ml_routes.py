def test_crop_recommendation(client, auth_headers):
    resp = client.post("/api/recommendations/crop", json={
        "nitrogen": 80, "phosphorus": 45, "potassium": 40, "temperature": 25,
        "humidity": 82, "ph": 6.2, "rainfall": 220, "soil_type": "clay",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "recommended_crop" in data
    assert 0 <= data["suitability_score"] <= 100
    assert len(data["top_recommendations"]) >= 1


def test_crop_recommendation_invalid_input(client, auth_headers):
    resp = client.post("/api/recommendations/crop", json={
        "nitrogen": -10, "phosphorus": 45, "potassium": 40, "temperature": 25,
        "humidity": 82, "ph": 6.2, "rainfall": 220,
    }, headers=auth_headers)
    assert resp.status_code == 422
    assert resp.json()["error"] == "VALIDATION_ERROR"


def test_yield_prediction(client, auth_headers):
    resp = client.post("/api/yield/predict", json={
        "crop": "wheat", "area_hectare": 2.0, "nitrogen": 100, "phosphorus": 50,
        "potassium": 40, "temperature": 18, "humidity": 55, "ph": 6.8, "rainfall": 75,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["yield_per_hectare"] >= 0
    assert data["estimated_total_yield"] >= 0


def test_fertilizer_recommendation(client, auth_headers):
    resp = client.post("/api/fertilizer/recommend", json={
        "crop": "rice", "nitrogen": 30, "phosphorus": 20, "potassium": 20, "ph": 6.0,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "recommended_fertilizer" in data
    assert data["disclaimer"]


def test_disease_prediction(client, auth_headers):
    resp = client.post("/api/disease/predict", json={
        "crop": "rice", "temperature": 28, "humidity": 90, "rainfall": 200,
        "soil_moisture": 80, "growth_stage": "flowering", "previous_disease_history": True,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["risk_level"] in ("low", "medium", "high")


def test_irrigation_recommendation(client, auth_headers):
    resp = client.post("/api/irrigation/recommend", json={
        "crop": "maize", "soil_moisture": 20, "temperature": 35, "humidity": 30,
        "rainfall": 0, "growth_stage": "flowering", "area_hectare": 1.0,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["irrigation_required"] is True
    assert data["water_status"] in ("Adequate", "Moderate", "Low", "Critical")


def test_disease_image_endpoint_not_yet_available(client, auth_headers):
    """The image-based disease detection path is a structural scaffold only
    (no CNN is trained/bundled yet) — it should fail gracefully with a 501
    and a clear error code, not a 500 or a silent wrong answer."""
    files = {"image": ("leaf.jpg", b"fake-image-bytes", "image/jpeg")}
    resp = client.post("/api/disease/predict-image", files=files, headers=auth_headers)
    assert resp.status_code == 501
    assert resp.json()["error"] == "IMAGE_MODEL_NOT_AVAILABLE"
