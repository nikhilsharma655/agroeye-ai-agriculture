import os


def test_webhook_requires_signature(client):
    resp = client.get("/api/webhooks/n8n/daily-summary")
    assert resp.status_code == 401
    assert resp.json()["error"] == "WEBHOOK_AUTH_ERROR"


def test_webhook_with_valid_signature(client):
    secret = os.environ["N8N_WEBHOOK_SHARED_SECRET"]
    resp = client.get("/api/webhooks/n8n/daily-summary", headers={"X-AgroEye-Signature": secret})
    assert resp.status_code == 200
    assert resp.json()["success"] is True
