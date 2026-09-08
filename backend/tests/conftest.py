import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///./test_agroeye.db"
os.environ["N8N_WEBHOOK_SHARED_SECRET"] = "test-webhook-secret"

from app.main import app
from app.database import Base, engine
# Ensure every model is registered on Base's metadata/registry before
# create_all / mapper configuration (mirrors app.database.init_db()).
from app.models import user, farm, crop, soil_record, weather_record, prediction, recommendation, alert, notification  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_agroeye.db"):
        os.remove("test_agroeye.db")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    client.post("/api/auth/register", json={
        "name": "Test Farmer", "email": "test@example.com", "password": "testpass123",
        "phone": "1234567890", "location": "Test Location", "farm_size": 2.0,
    })
    resp = client.post("/api/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    return resp.json()["data"]["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_farm(client, auth_headers):
    resp = client.post("/api/farms", json={
        "name": "Test Farm", "location": "Test Loc", "area": 2.5, "soil_type": "loamy",
        "soil_ph": 6.5, "nitrogen": 60, "phosphorus": 40, "potassium": 40,
        "moisture": 50, "temperature": 26, "humidity": 65, "current_crop": "rice",
    }, headers=auth_headers)
    return resp.json()["data"]
