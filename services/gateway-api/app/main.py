from fastapi import FastAPI, Header, HTTPException, Request
from typing import Optional
import httpx
import os
import uuid

app = FastAPI(title="gateway-api", version="1.0.0")

SERVICE_NAME = os.getenv("SERVICE_NAME", "gateway-api")

# For local dev, we’ll point to localhost ports.
# For EKS, we’ll switch these to Kubernetes service DNS names.
USERS_BASE_URL = os.getenv("USERS_BASE_URL", "http://localhost:8001")
BILLING_BASE_URL = os.getenv("BILLING_BASE_URL", "http://localhost:8002")


def require_tenant(x_tenant_id: Optional[str]) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-Id header")
    return x_tenant_id


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/ready")
async def ready():
    # simple downstream readiness check
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            u = await client.get(f"{USERS_BASE_URL}/health")
            b = await client.get(f"{BILLING_BASE_URL}/health")
            if u.status_code != 200 or b.status_code != 200:
                raise HTTPException(status_code=503, detail="Downstream not ready")
        except Exception:
            raise HTTPException(status_code=503, detail="Downstream not ready")
    return {"status": "ready", "service": SERVICE_NAME}


@app.post("/api/signup")
async def signup(payload: dict, x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(
            f"{USERS_BASE_URL}/signup",
            headers={"X-Tenant-Id": tenant_id},
            json=payload,
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.json())
    return r.json()


@app.get("/api/users/me")
async def me(x_tenant_id: Optional[str] = Header(default=None), x_user_email: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    if not x_user_email:
        raise HTTPException(status_code=400, detail="Missing X-User-Email header")

    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(
            f"{USERS_BASE_URL}/me",
            headers={"X-Tenant-Id": tenant_id, "X-User-Email": x_user_email},
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.json())
    return r.json()


@app.get("/api/billing/plan")
async def plan(x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(
            f"{BILLING_BASE_URL}/plan",
            headers={"X-Tenant-Id": tenant_id},
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.json())
    return r.json()


@app.post("/api/billing/subscribe")
async def subscribe(payload: dict, x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(
            f"{BILLING_BASE_URL}/subscribe",
            headers={"X-Tenant-Id": tenant_id},
            json=payload,
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.json())
    return r.json()
