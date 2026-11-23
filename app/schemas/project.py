from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    target_end_date: date | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    target_end_date: date | None = None


class ProjectProgress(BaseModel):
    total_tasks: int
    todo: int
    in_progress: int
    in_review: int
    done: int
    overdue: int
    completion_percentage: float


class ProjectOut(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: str | None
    target_end_date: date | None
    created_at: datetime
    progress: ProjectProgress | None = None

    model_config = {"from_attributes": True}