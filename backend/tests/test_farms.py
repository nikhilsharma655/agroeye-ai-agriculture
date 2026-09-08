def test_create_farm(client, auth_headers):
    resp = client.post("/api/farms", json={
        "name": "My Farm", "area": 1.5, "soil_type": "sandy", "nitrogen": 50,
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "My Farm"


def test_list_farms(client, auth_headers, sample_farm):
    resp = client.get("/api/farms", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


def test_get_farm(client, auth_headers, sample_farm):
    resp = client.get(f"/api/farms/{sample_farm['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == sample_farm["id"]


def test_get_farm_not_found(client, auth_headers):
    resp = client.get("/api/farms/does-not-exist", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["error"] == "FARM_NOT_FOUND"


def test_update_farm(client, auth_headers, sample_farm):
    resp = client.put(f"/api/farms/{sample_farm['id']}", json={"current_crop": "wheat"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["current_crop"] == "wheat"


def test_delete_farm(client, auth_headers, sample_farm):
    resp = client.delete(f"/api/farms/{sample_farm['id']}", headers=auth_headers)
    assert resp.status_code == 200
    resp2 = client.get(f"/api/farms/{sample_farm['id']}", headers=auth_headers)
    assert resp2.status_code == 404


def test_farm_insights(client, auth_headers, sample_farm):
    resp = client.get(f"/api/farms/{sample_farm['id']}/insights", headers=auth_headers)
    assert resp.status_code == 200
    insights = resp.json()["data"]["insights"]
    assert len(insights) >= 4
    categories = {i["category"] for i in insights}
    assert "soil" in categories and "irrigation" in categories
