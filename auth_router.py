from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from db_session import get_db
from models_entities import User, UserRole, UserStatus
from schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from core_security import hash_password, verify_password, make_token
from dependencies import current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.role == UserRole.ADMIN:
        raise HTTPException(403, "Administrator accounts are created by the system owner")
    if data.role == UserRole.STUDENT and not data.student_id:
        raise HTTPException(422, "Student ID is required")
    if data.role == UserRole.TEACHER and not data.staff_id:
        raise HTTPException(422, "Teacher/employee ID is required")
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    user = User(full_name=data.full_name.strip(), email=email,
                password_hash=hash_password(data.password), role=data.role,
                status=UserStatus.PENDING, preferred_language=data.preferred_language,
                student_id=data.student_id, staff_id=data.staff_id,
                department_id=data.department_id)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(403, f"Account is {user.status.value}; contact the administrator")
    return TokenResponse(access_token=make_token(user.id))

@router.get("/me", response_model=UserResponse)
def me(user=Depends(current_user)):
    return user
