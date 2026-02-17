from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import require_admin

router = APIRouter(prefix="/users", tags=["Users"])


# =========================
# Create User (ADMIN only)
# =========================

@router.post("/createUser", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# Login User
# =========================

@router.post("/login", response_model=schemas.TokenResponse)
def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == credentials.email
    ).first()

    if not user or not verify_password(
        credentials.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    print("User from DB:", user)


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# =========================
# Delete User (ADMIN only)
# =========================

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Delete a user (Admin only)
    """

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

# =========================
# Get All Users (Admin only)
# =========================

@router.get("/getAllUsers", response_model=list[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Admin can view all users
    """
    return db.query(models.User).all()

# =========================
# Get All Tech Leads (ADMIN only)
# =========================
@router.get("/getAllTechLeads", response_model=list[schemas.UserResponse])
def get_all_tech_leads(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Admin can view all Tech Leads
    """
    return db.query(models.User).filter(models.User.role == "TECH_LEAD").all()


# =========================
# Get User By ID (Admin only)
# =========================

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

