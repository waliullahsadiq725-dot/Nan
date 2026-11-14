from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from db_session import get_db
from models_entities import Faculty, Department

router = APIRouter(prefix="/catalog", tags=["Faculties and departments"])

@router.get("/faculties")
def faculties(db: Session = Depends(get_db)):
    return list(db.scalars(select(Faculty).order_by(Faculty.name_en)).all())

@router.get("/departments")
def departments(faculty_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Department)
    if faculty_id:
        query = query.where(Department.faculty_id == faculty_id)
    return list(db.scalars(query.order_by(Department.name_en)).all())
