from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime
import enum

class TaskStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REWORK = "rework"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HistoryEventType(str, enum.Enum):
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    COMMENT_ADDED = "comment_added"
    WORKER_COMPLETED = "worker_completed"
    APPROVED = "approved"
    RETURNED = "returned"

task_workers = Table(
    'task_workers',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('worker_id', Integer, primary_key=True)
)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.NEW)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    created_by = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    history = relationship("History", back_populates="task", cascade="all, delete-orphan")
    worker_completions = relationship("WorkerCompletion", back_populates="task", cascade="all, delete-orphan")
    
    @property
    def worker_ids(self):
        """Get list of assigned worker IDs from task_workers table"""
        from app.db.database import SessionLocal
        db = SessionLocal()
        try:
            result = db.query(task_workers).filter(task_workers.c.task_id == self.id).all()
            return [row[1] for row in result]
        finally:
            db.close()
    
    @property
    def worker_ids_list(self):
        """Alias for worker_ids"""
        return self.worker_ids
    
    @worker_ids_list.setter
    def worker_ids_list(self, values):
        """Placeholder setter - actual update handled by service"""
        pass

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer)
    full_name = Column(String, default="Unknown User")
    text = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    task = relationship("Task", back_populates="comments")

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    event_type = Column(SQLEnum(HistoryEventType))
    user_id = Column(Integer)
    details = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    task = relationship("Task", back_populates="history")

class WorkerCompletion(Base):
    __tablename__ = "worker_completions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    worker_id = Column(Integer)
    completed_at = Column(DateTime, server_default=func.now())
    
    task = relationship("Task", back_populates="worker_completions")
