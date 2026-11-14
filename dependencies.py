from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db_session import get_db
from models_entities import User, UserRole, UserStatus
from core_security import read_token
from core_config import settings

oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    user_id = read_token(token)
    if user_id is None:
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(401, "Account is not active")
    return user

def roles_allowed(*roles: UserRole):
    def dependency(user=Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return dependency
