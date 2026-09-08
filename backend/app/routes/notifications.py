from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", summary="List notifications for the current user")
def list_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = (
        db.query(Notification).filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc()).all()
    )
    data = [
        {"id": n.id, "title": n.title, "message": n.message, "type": n.notification_type,
         "is_read": n.is_read, "source": n.source, "created_at": n.created_at.isoformat()}
        for n in notifications
    ]
    return success_response("Notifications retrieved", data=data)


@router.put("/{notification_id}/read", summary="Mark a notification as read")
def mark_read(notification_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id,
                                           Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"success": False, "message": "Notification not found",
                                     "error": "NOTIFICATION_NOT_FOUND"})
    notif.is_read = True
    db.commit()
    return success_response("Notification marked as read")
