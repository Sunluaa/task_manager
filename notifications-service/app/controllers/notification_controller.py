from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationListResponse
from app.services.notification_service import NotificationService
from app.services.queue import NotificationQueue
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/", response_model=dict)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Enqueue notification for async processing"""
    try:
        task_id = await NotificationService.enqueue_notification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message
        )
        return {
            "task_id": task_id,
            "status": "enqueued",
            "message": "Notification queued for processing"
        }
    except Exception as e:
        logger.error(f"Error enqueueing notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue notification"
        )

@router.get("/user/{user_id}", response_model=NotificationListResponse)
async def get_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    notifications = NotificationService.get_user_notifications(db, user_id, skip, limit)
    unread_count = NotificationService.get_unread_count(db, user_id)
    return {
        "total": len(notifications),
        "unread_count": unread_count,
        "items": notifications
    }

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = NotificationService.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    notification = NotificationService.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    logger.info(f"Notification marked as read: {notification_id}")
    return notification

@router.put("/user/{user_id}/read-all")
async def mark_all_as_read(user_id: int, db: Session = Depends(get_db)):
    NotificationService.mark_all_as_read(db, user_id)
    logger.info(f"All notifications marked as read for user {user_id}")
    return {"detail": "All notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    if not NotificationService.delete_notification(db, notification_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    logger.info(f"Notification deleted: {notification_id}")
    return {"detail": "Notification deleted"}

@router.get("/user/{user_id}/unread-count")
async def get_unread_count(user_id: int, db: Session = Depends(get_db)):
    count = NotificationService.get_unread_count(db, user_id)
    return {"unread_count": count}

@router.get("/admin/queue-stats")
async def get_queue_stats():
    """Get queue statistics (admin endpoint)"""
    try:
        stats = await NotificationQueue.get_queue_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get queue stats"
        )
