from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from db_session import get_db
from models_entities import User, UserRole, UserStatus, Resource, ResourceStatus, Faculty, Department, Notification
from schemas import UserResponse, UserStatusRequest, ReviewRequest
from dependencies import roles_allowed

router = APIRouter(prefix="/admin", tags=["Administration"])
admin_user = roles_allowed(UserRole.ADMIN)

@router.get("/users", response_model=list[UserResponse])
def users(status: UserStatus | None = None, db: Session = Depends(get_db), admin=Depends(admin_user)):
    query = select(User).order_by(User.created_at.desc())
    if status:
        query = query.where(User.status == status)
    return list(db.scalars(query).all())

@router.patch("/users/{user_id}/status", response_model=UserResponse)
def set_user_status(user_id: int, data: UserStatusRequest, db: Session = Depends(get_db), admin=Depends(admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.id == admin.id and data.status != UserStatus.ACTIVE:
        raise HTTPException(400, "You cannot suspend your own administrator account")
    user.status = data.status
    db.commit(); db.refresh(user)
    return user

@router.get("/resources/pending", response_model=list)
def pending_resources(db: Session = Depends(get_db), admin=Depends(admin_user)):
    return list(db.scalars(select(Resource).where(Resource.status == ResourceStatus.PENDING)).all())

@router.patch("/resources/{resource_id}/review")
def review_resource(resource_id: int, data: ReviewRequest, db: Session = Depends(get_db), admin=Depends(admin_user)):
    if data.status == ResourceStatus.PENDING:
        raise HTTPException(422, "Choose approved or rejected")
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    resource.status = data.status
    db.add(Notification(user_id=resource.uploader_id, title="Library resource reviewed",
                        message=f"Your resource '{resource.title}' was {data.status.value}."))
    db.commit()
    return {"id": resource.id, "status": resource.status.value}

@router.post("/faculties", status_code=201)
def add_faculty(data: dict, db: Session = Depends(get_db), admin=Depends(admin_user)):
    faculty = Faculty(name_ps=data["name_ps"], name_dr=data["name_dr"], name_en=data["name_en"])
    db.add(faculty); db.commit(); db.refresh(faculty)
    return {"id": faculty.id}

@router.post("/departments", status_code=201)
def add_department(data: dict, db: Session = Depends(get_db), admin=Depends(admin_user)):
    if not db.get(Faculty, data["faculty_id"]):
        raise HTTPException(404, "Faculty not found")
    department = Department(faculty_id=data["faculty_id"], name_ps=data["name_ps"],
                            name_dr=data["name_dr"], name_en=data["name_en"])
    db.add(department); db.commit(); db.refresh(department)
    return {"id": department.id}

@router.get("/statistics")
def stats(db: Session = Depends(get_db), admin=Depends(admin_user)):
    count = lambda model, *conditions: db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0
    return {
        "users": count(User),
        "students": count(User, User.role == UserRole.STUDENT),
        "teachers": count(User, User.role == UserRole.TEACHER),
        "resources": count(Resource),
        "approved_resources": count(Resource, Resource.status == ResourceStatus.APPROVED),
        "pending_resources": count(Resource, Resource.status == ResourceStatus.PENDING)
    }
