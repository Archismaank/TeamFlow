from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import get_workspace_member
from app.core.ws import ws_manager
from app.models.models import (
    User,
    Project,
    Task,
    Comment,
    WorkspaceMember,
    TaskStatus,
    TaskPriority,
    RoleEnum,
)
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, CommentCreate, CommentOut

router = APIRouter(prefix="/api", tags=["tasks"])

WRITE_ROLES = [RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MEMBER]


async def _get_project_or_404(project_id: UUID, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _serialize_task(task: Task, db: AsyncSession) -> TaskOut:
    assignee_name = None
    if task.assignee_id:
        u_res = await db.execute(select(User.full_name).where(User.id == task.assignee_id))
        assignee_name = u_res.scalar_one_or_none()

    c_res = await db.execute(select(func.count(Comment.id)).where(Comment.task_id == task.id))
    comment_count = c_res.scalar_one() or 0

    return TaskOut(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assignee_id=task.assignee_id,
        assignee_name=assignee_name,
        due_date=task.due_date,
        position=task.position,
        created_at=task.created_at,
        comment_count=comment_count,
    )


@router.websocket("/ws/projects/{project_id}")
async def project_board_ws(websocket: WebSocket, project_id: str):
    await ws_manager.connect(project_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(project_id, websocket)


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: UUID,
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await _get_project_or_404(project_id, db)
    await get_workspace_member(project.workspace_id, db, current_user, allowed_roles=WRITE_ROLES)

    if payload.assignee_id:
        member_res = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == project.workspace_id,
                WorkspaceMember.user_id == payload.assignee_id,
            )
        )
        if not member_res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Assignee must be a member of this workspace")

    max_pos_res = await db.execute(
        select(func.coalesce(func.max(Task.position), -1)).where(
            Task.project_id == project_id,
            Task.status == payload.status,
        )
    )
    next_position = (max_pos_res.scalar_one() or 0) + 1

    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
        position=next_position,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    task_out = await _serialize_task(task, db)
    await ws_manager.broadcast(
        str(project_id),
        {"event": "TASK_CREATED", "task": task_out.model_dump(mode="json")},
    )
    return task_out


@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
async def list_tasks(
    project_id: UUID,
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = Query(default=None),
    assignee_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await _get_project_or_404(project_id, db)
    await get_workspace_member(project.workspace_id, db, current_user)

    query = select(Task).where(Task.project_id == project_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority:
        query = query.where(Task.priority == priority)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)

    query = query.order_by(Task.position.asc(), Task.created_at.asc())
    result = await db.execute(query)
    tasks = result.scalars().all()

    return [await _serialize_task(t, db) for t in tasks]


@router.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await get_workspace_member(task.project.workspace_id, db, current_user, allowed_roles=WRITE_ROLES)

    update_data = payload.model_dump(exclude_unset=True)
    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        member_res = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == task.project.workspace_id,
                WorkspaceMember.user_id == update_data["assignee_id"],
            )
        )
        if not member_res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Assignee must be a member of this workspace")

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    task_out = await _serialize_task(task, db)
    await ws_manager.broadcast(
        str(task.project_id),
        {"event": "TASK_UPDATED", "task": task_out.model_dump(mode="json")},
    )
    return task_out


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await get_workspace_member(task.project.workspace_id, db, current_user, allowed_roles=WRITE_ROLES)

    project_id = str(task.project_id)
    deleted_id = str(task.id)
    await db.delete(task)
    await db.commit()

    await ws_manager.broadcast(
        project_id,
        {"event": "TASK_DELETED", "task_id": deleted_id},
    )


@router.get("/tasks/{task_id}/comments", response_model=list[CommentOut])
async def list_comments(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await get_workspace_member(task.project.workspace_id, db, current_user)

    c_res = await db.execute(
        select(Comment, User.full_name)
        .join(User, Comment.author_id == User.id)
        .where(Comment.task_id == task_id)
        .order_by(Comment.created_at.asc())
    )
    return [
        CommentOut(
            id=comment.id,
            task_id=comment.task_id,
            author_id=comment.author_id,
            author_name=author_name,
            content=comment.content,
            created_at=comment.created_at,
        )
        for comment, author_name in c_res.all()
    ]


@router.post("/tasks/{task_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def add_comment(
    task_id: UUID,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await get_workspace_member(task.project.workspace_id, db, current_user, allowed_roles=WRITE_ROLES)

    comment = Comment(
        task_id=task_id,
        author_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    comment_out = CommentOut(
        id=comment.id,
        task_id=comment.task_id,
        author_id=comment.author_id,
        author_name=current_user.full_name,
        content=comment.content,
        created_at=comment.created_at,
    )
    await ws_manager.broadcast(
        str(task.project_id),
        {"event": "COMMENT_CREATED", "comment": comment_out.model_dump(mode="json")},
    )
    return comment_out