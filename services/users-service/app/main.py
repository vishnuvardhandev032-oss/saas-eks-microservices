from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import uuid

app = FastAPI(title="users-service", version="1.0.0")

SERVICE_NAME = os.getenv("SERVICE_NAME", "users-service")

def require_tenant(x_tenant_id: Optional[str]) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-Id header")
    return x_tenant_id

class SignupReq(BaseModel):
    email: str
    password: str

class LoginReq(BaseModel):
    email: str
    password: str

# Demo-only in-memory store
USERS = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}

@app.get("/ready")
def ready():
    return {"status": "ready", "service": SERVICE_NAME}

@app.post("/signup")
def signup(body: SignupReq, x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    key = f"{tenant_id}:{body.email}"
    if key in USERS:
        raise HTTPException(status_code=409, detail="User already exists")
    user_id = str(uuid.uuid4())
    USERS[key] = {"user_id": user_id, "email": body.email, "tenant_id": tenant_id}
    return {"message": "created", "user_id": user_id, "tenant_id": tenant_id}

@app.post("/login")
def login(body: LoginReq, x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    key = f"{tenant_id}:{body.email}"
    if key not in USERS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "logged_in", "user_id": USERS[key]["user_id"], "tenant_id": tenant_id}

@app.get("/me")
def me(x_tenant_id: Optional[str] = Header(default=None), x_user_email: Optional[str] = Header(default=None)):
    tenant_id = require_tenant(x_tenant_id)
    if not x_user_email:
        raise HTTPException(status_code=400, detail="Missing X-User-Email header")
    key = f"{tenant_id}:{x_user_email}"
    if key not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS[key]
