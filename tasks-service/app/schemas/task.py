from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REWORK = "rework"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HistoryEventType(str, Enum):
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    COMMENT_ADDED = "comment_added"
    WORKER_COMPLETED = "worker_completed"
    APPROVED = "approved"
    RETURNED = "returned"

class CommentCreate(BaseModel):
    text: str
    full_name: Optional[str] = "Unknown User"

class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    full_name: Optional[str] = "Unknown User"
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

class HistoryResponse(BaseModel):
    id: int
    task_id: int
    event_type: HistoryEventType
    user_id: int
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class WorkerCompletionResponse(BaseModel):
    id: int
    task_id: int
    worker_id: int
    completed_at: datetime

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    worker_ids: List[int] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    worker_ids: Optional[List[int]] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_by: int
    created_at: datetime
    updated_at: datetime
    worker_ids: List[int] = []
    comments: List[CommentResponse] = []
    history: List[HistoryResponse] = []
    worker_completions: List[WorkerCompletionResponse] = []

    class Config:
        from_attributes = True

class TaskDetailResponse(TaskResponse):
    pass

class TaskListResponse(BaseModel):
    total: int
    items: List[TaskResponse]
