from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, CommentCreate, CommentResponse,
    HistoryResponse, TaskStatus, WorkerCompletionResponse
)
from app.services.task_service import TaskService
from app.services.user_validator import UserValidator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), user_id: int = 1):
    # Validate that all workers are active
    if task.worker_ids:
        is_valid, error_message = UserValidator.validate_active_users(task.worker_ids)
        if not is_valid:
            logger.warning(f"Cannot create task: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
    
    db_task = TaskService.create_task(
        db,
        title=task.title,
        description=task.description,
        priority=task.priority,
        created_by=user_id,
        worker_ids=task.worker_ids
    )
    logger.info(f"Task created: {db_task.id}")
    return db_task

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus = None,
    db: Session = Depends(get_db)
):
    tasks = TaskService.get_all_tasks(db, skip, limit, status)
    return tasks

@router.get("/list")
async def get_all_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    tasks = TaskService.get_all_tasks(db, skip, limit, None)
    # Явно сериализуем в список словарей
    task_list = []
    for task in tasks:
        task_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "worker_ids": task.worker_ids or [],
            "worker_completions": [
                {"worker_id": wc.worker_id, "completed_at": wc.completed_at.isoformat() if wc.completed_at else None}
                for wc in (task.worker_completions or [])
            ] if hasattr(task, 'worker_completions') else [],
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        })
    return {"tasks": task_list}

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    # Validate that all new workers are active
    if task_update.worker_ids:
        is_valid, error_message = UserValidator.validate_active_users(task_update.worker_ids)
        if not is_valid:
            logger.warning(f"Cannot update task: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
    
    task = TaskService.update_task(
        db,
        task_id,
        title=task_update.title,
        description=task_update.description,
        status=task_update.status,
        priority=task_update.priority,
        worker_ids=task_update.worker_ids,
        updated_by=user_id
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info(f"Task updated: {task_id}")
    return task

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not TaskService.delete_task(db, task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info(f"Task deleted: {task_id}")
    return {"detail": "Task deleted"}

@router.post("/{task_id}/comments", response_model=CommentResponse)
async def add_comment(
    task_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    db_comment = TaskService.add_comment(db, task_id, user_id, comment.text, comment.full_name)
    logger.info(f"Comment added to task {task_id}")
    return db_comment

@router.post("/{task_id}/mark-completed", response_model=WorkerCompletionResponse)
async def mark_completed(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    completion = TaskService.mark_worker_completed(db, task_id, user_id)
    logger.info(f"Worker {user_id} marked task {task_id} as completed")
    return completion

@router.post("/{task_id}/approve", response_model=TaskResponse)
async def approve_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    task = TaskService.approve_task(db, task_id, user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info(f"Task approved: {task_id}")
    return task

@router.post("/{task_id}/return-rework", response_model=TaskResponse)
async def return_rework(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    task = TaskService.return_to_rework(db, task_id, user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info(f"Task returned to rework: {task_id}")
    return task

@router.get("/{task_id}/history", response_model=list[HistoryResponse])
async def get_task_history(task_id: int, db: Session = Depends(get_db)):
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task.history

@router.get("/{task_id}/comments", response_model=list[CommentResponse])
async def get_task_comments(task_id: int, db: Session = Depends(get_db)):
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task.comments

@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_user_to_task(task_id: int, worker_id: int, db: Session = Depends(get_db)):
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Add worker to task
    if worker_id not in task.worker_ids:
        task.worker_ids.append(worker_id)
        db.commit()
        db.refresh(task)
        logger.info(f"User {worker_id} assigned to task {task_id}")
    
    return task

@router.post("/{task_id}/unassign", response_model=TaskResponse)
async def unassign_user_from_task(task_id: int, worker_id: int, db: Session = Depends(get_db)):
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Remove worker from task
    if worker_id in task.worker_ids:
        task.worker_ids.remove(worker_id)
        db.commit()
        db.refresh(task)
        logger.info(f"User {worker_id} unassigned from task {task_id}")
    
    return task

@router.get("/{task_id}/workers", response_model=list[int])
async def get_task_workers(task_id: int, db: Session = Depends(get_db)):
    """Get all workers assigned to a task"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    workers = TaskService.get_task_workers(db, task_id)
    return workers

@router.post("/{task_id}/add-worker/{worker_id}", response_model=TaskResponse)
async def add_worker_to_task(
    task_id: int,
    worker_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Admin only: Add a worker to a task"""
    result = TaskService.add_worker_to_task(db, task_id, worker_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info(f"Worker {worker_id} added to task {task_id}")
    return result.get("task")

@router.post("/{task_id}/remove-worker/{worker_id}", response_model=TaskResponse)
async def remove_worker_from_task(
    task_id: int,
    worker_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Admin only: Remove a worker from a task"""
    result = TaskService.remove_worker_from_task(db, task_id, worker_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info(f"Worker {worker_id} removed from task {task_id}")
    return result.get("task")

@router.post("/{task_id}/complete")
async def complete_task_by_worker(
    task_id: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Worker: Mark task as completed"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    completion = TaskService.worker_complete_task(db, task_id, user_id)
    if not completion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this task"
        )
    
    logger.info(f"Worker {user_id} marked task {task_id} as completed")
    return {
        "id": completion.id,
        "task_id": completion.task_id,
        "worker_id": completion.worker_id,
        "completed_at": completion.completed_at.isoformat() if completion.completed_at else None
    }

@router.post("/{task_id}/approve")
async def approve_task_by_admin(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Query(1)
):
    """Admin: Approve task as completed"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    updated_task = TaskService.approve_task(db, task_id, user_id)
    if not updated_task:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Failed to approve task")
    
    logger.info(f"Admin {user_id} approved task {task_id}")
    return updated_task

@router.post("/{task_id}/rework")
async def send_task_to_rework(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Query(1)
):
    """Admin: Send task back to rework"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    updated_task = TaskService.send_to_rework(db, task_id, user_id)
    if not updated_task:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Failed to send task to rework")
    
    logger.info(f"Admin {user_id} sent task {task_id} to rework")
    return updated_task

