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


class UserSummaryResponse(BaseModel):
    total_users: int
    total_tech_leads: int
    total_admins: int


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
# OTP Schemas
# =========================

class OTPRequest(BaseModel):
    """Returned after successful email + password check."""
    message: str
    email: EmailStr


class OTPVerify(BaseModel):
    """Submitted by the user to verify the OTP."""
    email: EmailStr
    otp: str


# =========================
# Forgot Password Schemas
# =========================

class ForgotPasswordRequest(BaseModel):
    """Step 1 — user submits their email."""
    email: EmailStr


class ForgotPasswordVerify(BaseModel):
    """Step 2 — user submits the OTP they received."""
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    """Step 3 — user sets a new password using the reset token."""
    reset_token: str
    new_password: str


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


# =========================
# Pull Request Schemas
# =========================

class PullRequestOut(BaseModel):
    id: int
    title: str
    author: str
    state: str
    source_branch: str
    target_branch: str
    created_at: datetime
    days_open: int
    is_stale: bool
    url: str