# AgroEye × n8n Automation

This folder contains importable n8n workflow definitions that connect to the
AgroEye FastAPI backend via webhooks. The integration is intentionally kept
**loosely coupled**: n8n can be replaced or extended without touching any ML
model or backend business logic — every touchpoint is a plain HTTP webhook.

## How it fits together

```
AgroEye (FastAPI)  --outbound webhook-->  n8n  --notification-->  Farmer
AgroEye (FastAPI)  <--inbound webhook---  n8n  (daily summary pull, acks)
```

- **Outbound** (AgroEye → n8n): sent by `backend/app/services/n8n_service.py`
  whenever a high disease risk, low soil moisture, or new recommendation is
  detected. Configure the target URLs via `.env`:
  - `N8N_FARM_ALERT_WEBHOOK_URL`
  - `N8N_IRRIGATION_ALERT_WEBHOOK_URL`
  - `N8N_RECOMMENDATION_WEBHOOK_URL`
- **Inbound** (n8n → AgroEye): handled by `backend/app/routes/webhooks.py`
  under `/api/webhooks/n8n/*`, protected by a shared secret sent as the
  `X-AgroEye-Signature` header (`N8N_WEBHOOK_SHARED_SECRET`).

## Workflows included

| File | Trigger | Purpose |
|---|---|---|
| `1-farm-disease-alert.json` | Webhook `agroeye/farm-alert` | High disease-risk prediction → email/SMS the farmer, ack back to AgroEye |
| `2-irrigation-alert.json` | Webhook `agroeye/irrigation-alert` | Low/critical soil moisture → SMS/WhatsApp alert, log notification in AgroEye |
| `3-daily-farm-summary.json` | Schedule (daily 7 AM) | Pulls `/api/webhooks/n8n/daily-summary`, emails each farmer their farm snapshot |
| `4-new-recommendation-notify.json` | Webhook `agroeye/recommendation` | New crop/fertilizer/irrigation recommendation → push a notification |

## Setup

1. Start n8n (see root `docker-compose.yml`, or `npx n8n`).
2. In the n8n UI, go to **Workflows → Import from File** and import each JSON file.
3. Set these n8n environment variables (Settings → Variables, or `.env` for
   the n8n container):
   - `AGROEYE_API_BASE_URL` — e.g. `http://backend:8000`
   - `AGROEYE_WEBHOOK_SECRET` — must match `N8N_WEBHOOK_SHARED_SECRET` in the
     AgroEye backend `.env`
4. Configure the Email/Twilio credential nodes with your own provider
   credentials (these are placeholders — swap for SendGrid, SMTP, Twilio, etc.)
5. Activate each workflow. Copy each workflow's webhook URL into the
   corresponding AgroEye backend `.env` variable.

## Extending

Because every integration point is a generic HTTP webhook with a JSON body,
you can:
- Replace n8n entirely with Zapier, Make, or a custom worker — just point the
  `N8N_*_WEBHOOK_URL` env vars at the new endpoint.
- Add new automations (e.g. WhatsApp Business API, Slack, push notifications)
  by adding nodes downstream of the existing webhook triggers — no backend or
  ML code changes required.
