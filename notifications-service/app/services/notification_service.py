from sqlalchemy.orm import Session
from app.models.notification import Notification
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def create_notification(db: Session, user_id: int, title: str, message: str) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        logger.info(f"Notification created for user {user_id}")
        return notification

    @staticmethod
    def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> Notification:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int):
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True, "read_at": datetime.utcnow()})
        db.commit()

    @staticmethod
    def delete_notification(db: Session, notification_id: int) -> bool:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            db.delete(notification)
            db.commit()
            return True
        return False

    @staticmethod
    def get_notification(db: Session, notification_id: int) -> Notification:
        return db.query(Notification).filter(Notification.id == notification_id).first()
