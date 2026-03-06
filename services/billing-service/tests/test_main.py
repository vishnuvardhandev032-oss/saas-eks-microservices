from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_plan_requires_tenant():
    r = client.get("/plan")
    assert r.status_code == 400

def test_subscribe_flow():
    tenant = "tenant-1"
    r = client.get("/plan", headers={"X-Tenant-Id": tenant})
    assert r.status_code == 200
    assert r.json()["plan"]["name"] == "free"

    r2 = client.post("/subscribe", headers={"X-Tenant-Id": tenant}, json={"plan": "pro"})
    assert r2.status_code == 200

    r3 = client.get("/plan", headers={"X-Tenant-Id": tenant})
    assert r3.status_code == 200
    assert r3.json()["plan"]["name"] == "pro"
