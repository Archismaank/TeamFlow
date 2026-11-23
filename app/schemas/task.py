from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.models import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: UUID | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: UUID | None = None
    due_date: datetime | None = None
    position: int | None = None


class TaskOut(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee_id: UUID | None
    assignee_name: str | None = None
    due_date: datetime | None
    position: int
    created_at: datetime
    comment_count: int = 0

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: UUID
    task_id: UUID
    author_id: UUID
    author_name: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}