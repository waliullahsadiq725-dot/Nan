from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, BigInteger, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db_session import Base

def now_utc():
    return datetime.now(timezone.utc)

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class ResourceStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, native_enum=False), index=True)
    status: Mapped[UserStatus] = mapped_column(SAEnum(UserStatus, native_enum=False), default=UserStatus.PENDING, index=True)
    preferred_language: Mapped[str] = mapped_column(String(5), default="ps")
    student_id: Mapped[str | None] = mapped_column(String(60), unique=True, nullable=True)
    staff_id: Mapped[str | None] = mapped_column(String(60), unique=True, nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class Faculty(Base):
    __tablename__ = "faculties"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_ps: Mapped[str] = mapped_column(String(180))
    name_dr: Mapped[str] = mapped_column(String(180))
    name_en: Mapped[str] = mapped_column(String(180))
    departments = relationship("Department", back_populates="faculty", cascade="all, delete-orphan")

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"))
    name_ps: Mapped[str] = mapped_column(String(180))
    name_dr: Mapped[str] = mapped_column(String(180))
    name_en: Mapped[str] = mapped_column(String(180))
    faculty = relationship("Faculty", back_populates="departments")

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(250), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    filename_original: Mapped[str] = mapped_column(String(255))
    filename_stored: Mapped[str] = mapped_column(String(80), unique=True)
    file_size: Mapped[int] = mapped_column(BigInteger)
    category: Mapped[str] = mapped_column(String(60), default="lecture")
    language: Mapped[str] = mapped_column(String(5), default="ps")
    status: Mapped[ResourceStatus] = mapped_column(SAEnum(ResourceStatus, native_enum=False), default=ResourceStatus.PENDING, index=True)
    uploader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    uploader = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    target: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
