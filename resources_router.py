import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from db_session import get_db
from models_entities import User, UserRole, Resource, ResourceStatus
from schemas import ResourceResponse
from dependencies import current_user, roles_allowed
from core_config import settings

router = APIRouter(prefix="/resources", tags=["Digital Library"])
can_upload = roles_allowed(UserRole.ADMIN, UserRole.TEACHER)

@router.get("", response_model=list[ResourceResponse])
def browse(q: str | None = Query(None, max_length=120), category: str | None = None,
           department_id: int | None = None, skip: int = 0,
           limit: int = Query(24, ge=1, le=100),
           db: Session = Depends(get_db), user=Depends(current_user)):
    query = select(Resource).where(Resource.status == ResourceStatus.APPROVED)
    if q:
        term = f"%{q.strip()}%"
        query = query.where(or_(Resource.title.ilike(term), Resource.description.ilike(term)))
    if category:
        query = query.where(Resource.category == category)
    if department_id:
        query = query.where(Resource.department_id == department_id)
    return list(db.scalars(query.order_by(Resource.created_at.desc()).offset(skip).limit(limit)).all())

@router.post("", response_model=ResourceResponse, status_code=201)
async def upload(title: str = Form(...), description: str | None = Form(None),
                 category: str = Form("lecture"), language: str = Form("ps"),
                 department_id: int | None = Form(None), file: UploadFile = File(...),
                 db: Session = Depends(get_db), user=Depends(can_upload)):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(415, "Only PDF files are allowed")
    storage = Path(settings.FILE_STORAGE_PATH)
    storage.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.pdf"
    destination = storage / stored_name
    size = 0
    signature = b""
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                if not signature:
                    signature = chunk[:5]
                size += len(chunk)
                if size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise HTTPException(413, "PDF exceeds maximum upload size")
                output.write(chunk)
        if signature != b"%PDF-":
            raise HTTPException(415, "File content is not a valid PDF")
        resource = Resource(title=title.strip(), description=description,
            filename_original=Path(file.filename).name[:255], filename_stored=stored_name,
            file_size=size, category=category, language=language,
            uploader_id=user.id, department_id=department_id,
            status=ResourceStatus.PENDING)
        db.add(resource); db.commit(); db.refresh(resource)
        return resource
    except Exception:
        if destination.exists():
            destination.unlink()
        raise
    finally:
        await file.close()

def visible_resource(resource_id: int, db: Session, user: User):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    if resource.status != ResourceStatus.APPROVED and user.role != UserRole.ADMIN and resource.uploader_id != user.id:
        raise HTTPException(404, "Resource not found")
    return resource

@router.get("/mine", response_model=list[ResourceResponse])
def mine(db: Session = Depends(get_db), user=Depends(can_upload)):
    return list(db.scalars(select(Resource).where(Resource.uploader_id == user.id).order_by(Resource.created_at.desc())).all())

@router.get("/{resource_id}", response_model=ResourceResponse)
def details(resource_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    resource = visible_resource(resource_id, db, user)
    resource.views += 1
    db.commit(); db.refresh(resource)
    return resource

@router.get("/{resource_id}/view")
def view_pdf(resource_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    resource = visible_resource(resource_id, db, user)
    path = Path(settings.FILE_STORAGE_PATH) / resource.filename_stored
    if not path.is_file():
        raise HTTPException(404, "PDF file not found")
    return FileResponse(path, media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{resource.filename_original}"'})

@router.get("/{resource_id}/download")
def download_pdf(resource_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    resource = visible_resource(resource_id, db, user)
    path = Path(settings.FILE_STORAGE_PATH) / resource.filename_stored
    if not path.is_file():
        raise HTTPException(404, "PDF file not found")
    resource.downloads += 1
    db.commit()
    return FileResponse(path, media_type="application/pdf", filename=resource.filename_original)
