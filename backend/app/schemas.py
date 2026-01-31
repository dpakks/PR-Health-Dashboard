from pydantic import BaseModel, EmailStr
from datetime import datetime


# =========================
# User Schemas
# =========================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================
# Auth Schemas
# =========================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =========================
# Project Schemas
# =========================

class ProjectCreate(BaseModel):
    name: str
    repo_url: str


class ProjectOut(BaseModel):
    id: int
    name: str
    repo_url: str
    created_by: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
