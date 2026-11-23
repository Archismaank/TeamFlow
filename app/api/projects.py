from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import get_workspace_member
from app.models.models import User, Project, Task, TaskStatus, RoleEnum
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectProgress

router = APIRouter(prefix="/api", tags=["projects"])


def compute_project_progress(tasks: list[Task]) -> ProjectProgress:
    now = datetime.now(timezone.utc)
    total = len(tasks)
    todo = sum(1 for t in tasks if t.status == TaskStatus.TODO)
    in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
    in_review = sum(1 for t in tasks if t.status == TaskStatus.IN_REVIEW)
    done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
    overdue = sum(
        1 for t in tasks if t.due_date and t.due_date < now and t.status != TaskStatus.DONE
    )
    completion = round((done / total) * 100, 1) if total > 0 else 0.0

    return ProjectProgress(
        total_tasks=total,
        todo=todo,
        in_progress=in_progress,
        in_review=in_review,
        done=done,
        overdue=overdue,
        completion_percentage=completion,
    )


@router.post("/workspaces/{workspace_id}/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: UUID,
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_workspace_member(workspace_id, db, current_user, allowed_roles=[RoleEnum.OWNER, RoleEnum.ADMIN])

    project = Project(
        workspace_id=workspace_id,
        name=payload.name,
        description=payload.description,
        target_end_date=payload.target_end_date,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectOut(
        id=project.id,
        workspace_id=project.workspace_id,
        name=project.name,
        description=project.description,
        target_end_date=project.target_end_date,
        created_at=project.created_at,
        progress=compute_project_progress([]),
    )


@router.get("/workspaces/{workspace_id}/projects", response_model=list[ProjectOut])
async def list_projects(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_workspace_member(workspace_id, db, current_user)

    result = await db.execute(
        select(Project)
        .options(selectinload(Project.tasks))
        .where(Project.workspace_id == workspace_id)
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    return [
        ProjectOut(
            id=p.id,
            workspace_id=p.workspace_id,
            name=p.name,
            description=p.description,
            target_end_date=p.target_end_date,
            created_at=p.created_at,
            progress=compute_project_progress(p.tasks),
        )
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project).options(selectinload(Project.tasks)).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await get_workspace_member(project.workspace_id, db, current_user)

    return ProjectOut(
        id=project.id,
        workspace_id=project.workspace_id,
        name=project.name,
        description=project.description,
        target_end_date=project.target_end_date,
        created_at=project.created_at,
        progress=compute_project_progress(project.tasks),
    )


@router.patch("/projects/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project).options(selectinload(Project.tasks)).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await get_workspace_member(project.workspace_id, db, current_user, allowed_roles=[RoleEnum.OWNER, RoleEnum.ADMIN])

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    return ProjectOut(
        id=project.id,
        workspace_id=project.workspace_id,
        name=project.name,
        description=project.description,
        target_end_date=project.target_end_date,
        created_at=project.created_at,
        progress=compute_project_progress(project.tasks),
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await get_workspace_member(project.workspace_id, db, current_user, allowed_roles=[RoleEnum.OWNER, RoleEnum.ADMIN])

    await db.delete(project)
    await db.commit()