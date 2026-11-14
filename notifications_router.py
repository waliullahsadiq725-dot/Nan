from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from db_session import get_db
from models_entities import Notification
from dependencies import current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def my_notifications(db: Session = Depends(get_db), user=Depends(current_user)):
    return list(db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100)).all())

@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    item = db.get(Notification, notification_id)
    if not item or item.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    item.is_read = True
    db.commit()
    return {"message": "Marked as read"}
