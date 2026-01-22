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

# =============================
# Project Schemas
# =============================

class ProjectCreate(BaseModel):
    project_name: str
    github_org: str
    repo_name: str


# class ProjectOut(BaseModel):
#     id: int
#     project_name: str
#     github_org: str
#     repo_name: str

#     class Config:
#         orm_mode = True

class ProjectOut(BaseModel):
    id: int
    project_name: str
    github_org: str
    repo_name: str

    model_config = {
        "from_attributes": True
    }

#     orm_mode was used in Pydantic v1 to tell Pydantic it can read data from ORM (SQLAlchemy) objects.
# In Pydantic v2, this was renamed to from_attributes, and the old syntax was deprecated.
# So when you use model_config = {"from_attributes": True}, you’re using the correct new way, which removes the warning.
# Both do the same job — only the syntax changed.


