"""
Handles outbound webhook calls from AgroEye to n8n. Kept as a thin, isolated
service so n8n can be swapped/extended (e.g. for a different automation
engine) without touching ML models, routes, or the rest of the business logic.
"""
import logging
import httpx
from app.config import settings

logger = logging.getLogger("agroeye.n8n")


def _post_webhook(url: str, payload: dict) -> bool:
    if not url:
        logger.info("n8n webhook URL not configured; skipping dispatch. Payload=%s", payload)
        return False
    try:
        headers = {"X-AgroEye-Signature": settings.N8N_WEBHOOK_SHARED_SECRET}
        response = httpx.post(url, json=payload, headers=headers, timeout=5.0)
        response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        logger.warning("n8n webhook dispatch failed (%s): %s", url, exc)
        return False


def send_farm_alert(farm_id: str, alert_type: str, severity: str, message: str, payload: dict | None = None):
    body = {
        "event": "farm_alert",
        "farm_id": farm_id,
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "payload": payload or {},
    }
    return _post_webhook(settings.N8N_FARM_ALERT_WEBHOOK_URL, body)


def send_irrigation_alert(farm_id: str, water_status: str, estimated_requirement_litres: dict):
    body = {
        "event": "irrigation_alert",
        "farm_id": farm_id,
        "water_status": water_status,
        "estimated_requirement_litres": estimated_requirement_litres,
    }
    return _post_webhook(settings.N8N_IRRIGATION_ALERT_WEBHOOK_URL, body)


def send_recommendation_created(farm_id: str, category: str, summary: str):
    body = {
        "event": "recommendation_created",
        "farm_id": farm_id,
        "category": category,
        "summary": summary,
    }
    return _post_webhook(settings.N8N_RECOMMENDATION_WEBHOOK_URL, body)
