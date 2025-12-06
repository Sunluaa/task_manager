from sqlalchemy.orm import Session
from sqlalchemy import insert, delete as sql_delete
from app.models.task import Task, Comment, History, WorkerCompletion, TaskStatus, TaskPriority, HistoryEventType, task_workers
from app.db.database import SessionLocal
import logging
import json

logger = logging.getLogger(__name__)

class TaskService:
    @staticmethod
    def create_task(db: Session, title: str, description: str, priority: TaskPriority, 
                   created_by: int, worker_ids: list = None) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            created_by=created_by,
            status=TaskStatus.NEW
        )
        db.add(task)
        db.flush()
        
        # Store worker IDs
        if worker_ids:
            task.worker_ids_list = worker_ids
        
        # Add history event
        history = History(
            task_id=task.id,
            event_type=HistoryEventType.CREATED,
            user_id=created_by,
            details=json.dumps({"title": title, "priority": priority})
        )
        db.add(history)
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_all_tasks(db: Session, skip: int = 0, limit: int = 100, status: TaskStatus = None):
        query = db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_task_by_worker(db: Session, worker_id: int, skip: int = 0, limit: int = 100):
        # This is simplified - in production use proper many-to-many relationship
        from sqlalchemy import and_
        query = db.query(Task).filter(
            Task.id.in_(
                db.query(Task.id).filter(
                    Task.id.in_(
                        db.query(WorkerCompletion.task_id).filter(
                            WorkerCompletion.worker_id == worker_id
                        )
                    )
                )
            )
        ).offset(skip).limit(limit)
        return query.all()

    @staticmethod
    def update_task(db: Session, task_id: int, title: str = None, description: str = None,
                   status: TaskStatus = None, priority: TaskPriority = None,
                   worker_ids: list = None, updated_by: int = None) -> Task:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        if title:
            task.title = title
        if description:
            task.description = description
        if priority:
            task.priority = priority
        
        if status and status != task.status:
            old_status = task.status
            task.status = status
            history = History(
                task_id=task_id,
                event_type=HistoryEventType.STATUS_CHANGED,
                user_id=updated_by,
                details=json.dumps({"from": old_status, "to": status})
            )
            db.add(history)
        
        if worker_ids is not None:
            task.worker_ids_list = worker_ids
            if updated_by:
                history = History(
                    task_id=task_id,
                    event_type=HistoryEventType.ASSIGNED,
                    user_id=updated_by,
                    details=json.dumps({"worker_ids": worker_ids})
                )
                db.add(history)
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def add_comment(db: Session, task_id: int, user_id: int, text: str, full_name: str = "Unknown User") -> Comment:
        comment = Comment(
            task_id=task_id,
            user_id=user_id,
            full_name=full_name,
            text=text
        )
        db.add(comment)
        
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.COMMENT_ADDED,
            user_id=user_id,
            details=json.dumps({"comment": text, "author": full_name})
        )
        db.add(history)
        
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def mark_worker_completed(db: Session, task_id: int, worker_id: int) -> WorkerCompletion:
        existing = db.query(WorkerCompletion).filter(
            WorkerCompletion.task_id == task_id,
            WorkerCompletion.worker_id == worker_id
        ).first()
        
        if existing:
            return existing
        
        completion = WorkerCompletion(
            task_id=task_id,
            worker_id=worker_id
        )
        db.add(completion)
        
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.WORKER_COMPLETED,
            user_id=worker_id,
            details=json.dumps({"worker_id": worker_id})
        )
        db.add(history)
        
        db.commit()
        db.refresh(completion)
        return completion

    @staticmethod
    def approve_task(db: Session, task_id: int, approved_by: int) -> Task:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.APPROVED,
            user_id=approved_by,
            details=json.dumps({"action": "approved"})
        )
        db.add(history)
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def return_to_rework(db: Session, task_id: int, returned_by: int) -> Task:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        task.status = TaskStatus.REWORK
        
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.RETURNED,
            user_id=returned_by,
            details=json.dumps({"action": "returned_to_rework"})
        )
        db.add(history)
        
        # Clear worker completions for rework
        db.query(WorkerCompletion).filter(WorkerCompletion.task_id == task_id).delete()
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        db.delete(task)
        db.commit()
        return True

    @staticmethod
    def get_task_with_workers(db: Session, task_id: int) -> dict:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Get worker IDs from some mechanism (stored in task or separate table)
        worker_ids = getattr(task, 'worker_ids_list', [])
        
        return {
            "task": task,
            "worker_ids": worker_ids,
            "comments": task.comments,
            "history": task.history,
            "worker_completions": task.worker_completions
        }

    @staticmethod
    def add_worker_to_task(db: Session, task_id: int, worker_id: int, added_by: int) -> dict:
        """Add a worker to a task (admin only)"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Check if worker is already assigned
        existing = db.query(task_workers).filter(
            task_workers.c.task_id == task_id,
            task_workers.c.worker_id == worker_id
        ).first()
        
        if not existing:
            # Add worker to task
            stmt = insert(task_workers).values(task_id=task_id, worker_id=worker_id)
            db.execute(stmt)
            
            # Add history event
            history = History(
                task_id=task_id,
                event_type=HistoryEventType.ASSIGNED,
                user_id=added_by,
                details=json.dumps({"worker_id": worker_id, "action": "added"})
            )
            db.add(history)
            db.commit()
        
        db.refresh(task)
        return {"task": task, "worker_id": worker_id, "message": "Worker added to task"}

    @staticmethod
    def remove_worker_from_task(db: Session, task_id: int, worker_id: int, removed_by: int) -> dict:
        """Remove a worker from a task (admin only)"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Remove worker from task
        stmt = sql_delete(task_workers).where(
            (task_workers.c.task_id == task_id) & 
            (task_workers.c.worker_id == worker_id)
        )
        db.execute(stmt)
        
        # Add history event
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.ASSIGNED,
            user_id=removed_by,
            details=json.dumps({"worker_id": worker_id, "action": "removed"})
        )
        db.add(history)
        db.commit()
        
        db.refresh(task)
        return {"task": task, "worker_id": worker_id, "message": "Worker removed from task"}

    @staticmethod
    def get_task_workers(db: Session, task_id: int) -> list:
        """Get all workers assigned to a task"""
        result = db.query(task_workers).filter(task_workers.c.task_id == task_id).all()
        return [row[1] for row in result]

    @staticmethod
    def get_worker_tasks(db: Session, worker_id: int, skip: int = 0, limit: int = 100) -> list:
        """Get all tasks assigned to a worker"""
        task_ids = db.query(task_workers.c.task_id).filter(
            task_workers.c.worker_id == worker_id
        ).all()
        task_ids = [row[0] for row in task_ids]
        
        
        if not task_ids:
            return []
        
        return db.query(Task).filter(Task.id.in_(task_ids)).offset(skip).limit(limit).all()

    @staticmethod
    def worker_complete_task(db: Session, task_id: int, worker_id: int) -> WorkerCompletion:
        """Mark a task as completed by a worker"""
        # Check if worker is assigned to this task
        is_assigned = db.query(task_workers).filter(
            (task_workers.c.task_id == task_id) &
            (task_workers.c.worker_id == worker_id)
        ).first()
        
        if not is_assigned:
            return None
        
        # Check if already marked as completed
        existing = db.query(WorkerCompletion).filter(
            WorkerCompletion.task_id == task_id,
            WorkerCompletion.worker_id == worker_id
        ).first()
        
        if existing:
            return existing
        
        # Mark as completed
        completion = WorkerCompletion(
            task_id=task_id,
            worker_id=worker_id
        )
        db.add(completion)
        
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.WORKER_COMPLETED,
            user_id=worker_id,
            details=json.dumps({"worker_id": worker_id})
        )
        db.add(history)
        
        db.commit()
        db.refresh(completion)
        return completion

    @staticmethod
    def approve_task(db: Session, task_id: int, admin_id: int) -> Task:
        """Admin: Approve task as completed"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.APPROVED,
            user_id=admin_id,
            details=json.dumps({"action": "task_approved"})
        )
        db.add(history)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def send_to_rework(db: Session, task_id: int, admin_id: int) -> Task:
        """Admin: Send task back to rework"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        task.status = TaskStatus.REWORK
        
        # Clear worker completions to reset progress
        db.query(WorkerCompletion).filter(WorkerCompletion.task_id == task_id).delete()
        
        history = History(
            task_id=task_id,
            event_type=HistoryEventType.RETURNED,
            user_id=admin_id,
            details=json.dumps({"action": "task_returned_to_rework"})
        )
        db.add(history)
        db.commit()
        db.refresh(task)
        return task

