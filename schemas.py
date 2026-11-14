from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from models_entities import UserRole, UserStatus, ResourceStatus

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=160)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    role: UserRole
    preferred_language: str = "ps"
    student_id: str | None = None
    staff_id: str | None = None
    department_id: int | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str
    role: UserRole
    status: UserStatus
    preferred_language: str
    student_id: str | None
    staff_id: str | None
    department_id: int | None
    created_at: datetime

class UserStatusRequest(BaseModel):
    status: UserStatus

class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    filename_original: str
    file_size: int
    category: str
    language: str
    status: ResourceStatus
    uploader_id: int
    department_id: int | None
    downloads: int
    views: int
    created_at: datetime

class ReviewRequest(BaseModel):
    status: ResourceStatus
