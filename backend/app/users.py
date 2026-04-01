from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.dependencies import require_admin
from app.services.otp_service import generate_otp, store_otp, verify_otp
from app.services.ses_service import SESService

router = APIRouter(prefix="/users", tags=["Users"])

ses = SESService()


# =============================================================
# LOGIN FLOW  (Step 1 → Step 2)
# =============================================================

# Step 1: Validate credentials → send OTP
@router.post("/login", response_model=schemas.OTPRequest)
def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Validate email + password.
    On success, generate an OTP, send it via SES, and return a message.
    The client must then call /users/verify-otp to get the JWT.
    """

    user = db.query(models.User).filter(
        models.User.email == credentials.email
    ).first()

    if not user or not verify_password(
        credentials.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    otp = generate_otp()
    store_otp(user.email, otp, purpose="login")

    sent = ses.send_otp_email(
        recipient=user.email, otp=otp, purpose="login"
    )

    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please try again.",
        )

    return {
        "message": "OTP sent to your email",
        "email": user.email,
    }


# Step 2: Verify OTP → return JWT
@router.post("/verify-otp", response_model=schemas.TokenResponse)
def verify_login_otp(
    body: schemas.OTPVerify,
    db: Session = Depends(get_db),
):
    """
    Verify the OTP for login.
    On success, return a JWT access token.
    """

    try:
        valid = verify_otp(body.email, body.otp, purpose="login")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )

    user = db.query(models.User).filter(
        models.User.email == body.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =============================================================
# FORGOT PASSWORD FLOW  (Step 1 → Step 2 → Step 3)
# =============================================================

# Step 1: Submit email → receive OTP
@router.post("/forgot-password", response_model=schemas.OTPRequest)
def forgot_password(
    body: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Verify that the email exists, then send an OTP for password reset.
    """

    user = db.query(models.User).filter(
        models.User.email == body.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email",
        )

    otp = generate_otp()
    store_otp(user.email, otp, purpose="forgot_password")

    sent = ses.send_otp_email(
        recipient=user.email, otp=otp, purpose="forgot_password"
    )

    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please try again.",
        )

    return {
        "message": "OTP sent to your email",
        "email": user.email,
    }


# Step 2: Verify OTP → return a short-lived reset token
@router.post("/verify-forgot-otp")
def verify_forgot_password_otp(
    body: schemas.ForgotPasswordVerify,
    db: Session = Depends(get_db),
):
    """
    Verify the forgot-password OTP.
    On success, return a short-lived reset_token (JWT, 10 min).
    """

    try:
        valid = verify_otp(body.email, body.otp, purpose="forgot_password")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )

    user = db.query(models.User).filter(
        models.User.email == body.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    from datetime import timedelta

    reset_token = create_access_token(
        data={"sub": str(user.id), "purpose": "reset_password"},
        expires_delta=timedelta(minutes=10),
    )

    return {
        "message": "OTP verified. Use the reset token to set a new password.",
        "reset_token": reset_token,
    }


# Step 3: Reset password using the reset token
@router.post("/reset-password")
def reset_password(
    body: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Accept a reset_token + new_password.
    Validate the token, update the password hash, and return a JWT
    so the user is logged in immediately.
    """

    from jose import JWTError, jwt
    from app.config import settings

    try:
        payload = jwt.decode(
            body.reset_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("purpose") != "reset_password":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token",
            )

        user_id = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token",
        )

    user = db.query(models.User).filter(
        models.User.id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = hash_password(body.new_password)
    db.commit()

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return {
        "message": "Password reset successful",
        "access_token": access_token,
        "token_type": "bearer",
    }


# =============================================================
# EXISTING ENDPOINTS (unchanged)
# =============================================================

# Create User (ADMIN only)
@router.post("/createUser", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Delete User (ADMIN only)
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


# Get All Users (Admin only)
@router.get("/getAllUsers", response_model=list[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return db.query(models.User).all()


# Get All Tech Leads (ADMIN only)
@router.get("/getAllTechLeads", response_model=list[schemas.UserResponse])
def get_all_tech_leads(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return db.query(models.User).filter(
        models.User.role == "TECH_LEAD"
    ).all()


# Get User Summary (ADMIN only)
@router.get("/summary", response_model=schemas.UserSummaryResponse)
def get_user_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    total_users = db.query(models.User).count()
    total_tech_leads = db.query(models.User).filter(
        models.User.role == "TECH_LEAD"
    ).count()
    total_admins = db.query(models.User).filter(
        models.User.role == "ADMIN"
    ).count()

    return {
        "total_users": total_users,
        "total_tech_leads": total_tech_leads,
        "total_admins": total_admins,
    }


# Get User By ID (Admin only)
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user