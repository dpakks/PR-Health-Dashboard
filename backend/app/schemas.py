from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# =========================
# User Schemas
# =========================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # ADMIN or TECH_LEAD


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# Login Schemas
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


class ProjectResponse(BaseModel):
    id: int
    name: str
    repo_url: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
