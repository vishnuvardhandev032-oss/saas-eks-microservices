from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="billing-service", version="1.0.0")
SERVICE_NAME = os.getenv("SERVICE_NAME", "billing-service")

PLANS = {
    "free": {"name": "free", "price": 0, "features": ["basic"]},
    "pro": {"name": "pro", "price": 19, "features": ["basic", "teams", "priority-support"]},
}

# Demo in-memory tenant subscriptions
TENANT_SUBS = {}  # tenant_id -> plan


def require_tenant(x_tenant_id: Optional[str]) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-Id header")
    return x_tenant_id


class SubscribeReq(BaseModel):
    plan: str


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/ready")
def ready():
    return {"status": "ready", "service": SERVICE_NAME}


@app.get("/plan")
def get_plan(x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    plan = TENANT_SUBS.get(tenant_id, "free")
    return {"tenant_id": tenant_id, "plan": PLANS[plan]}


@app.post("/subscribe")
def subscribe(body: SubscribeReq, x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    if body.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    TENANT_SUBS[tenant_id] = body.plan
    return {"message": "subscribed", "tenant_id": tenant_id, "plan": PLANS[body.plan]}
