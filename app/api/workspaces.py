from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import get_workspace_member
from app.models.models import User, Workspace, WorkspaceMember, RoleEnum
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceOut,
    MemberInvite,
    MemberRoleUpdate,
    WorkspaceMemberOut,
)

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = Workspace(name=payload.name, owner_id=current_user.id)
    db.add(workspace)
    await db.flush()

    owner_member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role=RoleEnum.OWNER,
    )
    db.add(owner_member)
    await db.commit()
    await db.refresh(workspace)

    return WorkspaceOut(
        id=workspace.id,
        name=workspace.name,
        owner_id=workspace.owner_id,
        created_at=workspace.created_at,
        role=RoleEnum.OWNER,
    )


@router.get("", response_model=list[WorkspaceOut])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Workspace, WorkspaceMember.role)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == current_user.id)
        .order_by(Workspace.created_at.desc())
    )
    return [
        WorkspaceOut(
            id=ws.id,
            name=ws.name,
            owner_id=ws.owner_id,
            created_at=ws.created_at,
            role=role,
        )
        for ws, role in result.all()
    ]


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberOut])
async def list_workspace_members(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_workspace_member(workspace_id, db, current_user)

    result = await db.execute(
        select(WorkspaceMember)
        .options(selectinload(WorkspaceMember.user))
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    members = result.scalars().all()
    return [
        WorkspaceMemberOut(
            user_id=m.user.id,
            full_name=m.user.full_name,
            email=m.user.email,
            role=m.role,
        )
        for m in members
    ]


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberOut, status_code=status.HTTP_201_CREATED)
async def add_workspace_member(
    workspace_id: UUID,
    payload: MemberInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_workspace_member(workspace_id, db, current_user, allowed_roles=[RoleEnum.OWNER, RoleEnum.ADMIN])

    user_res = await db.execute(select(User).where(User.email == payload.email))
    target_user = user_res.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="No registered user found with that email")

    existing_res = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == target_user.id,
        )
    )
    if existing_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already in this workspace")

    if payload.role == RoleEnum.OWNER:
        raise HTTPException(status_code=400, detail="Cannot assign OWNER role via invite")

    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=target_user.id,
        role=payload.role,
    )
    db.add(member)
    await db.commit()

    return WorkspaceMemberOut(
        user_id=target_user.id,
        full_name=target_user.full_name,
        email=target_user.email,
        role=member.role,
    )


@router.patch("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberOut)
async def update_member_role(
    workspace_id: UUID,
    user_id: UUID,
    payload: MemberRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_workspace_member(workspace_id, db, current_user, allowed_roles=[RoleEnum.OWNER, RoleEnum.ADMIN])

    result = await db.execute(
        select(WorkspaceMember)
        .options(selectinload(WorkspaceMember.user))
        .where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == RoleEnum.OWNER:
        raise HTTPException(status_code=400, detail="Cannot modify the workspace owner's role")

    member.role = payload.role
    await db.commit()

    return WorkspaceMemberOut(
        user_id=member.user.id,
        full_name=member.user.full_name,
        email=member.user.email,
        role=member.role,
    )


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_workspace_member(
    workspace_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_workspace_member(workspace_id, db, current_user, allowed_roles=[RoleEnum.OWNER, RoleEnum.ADMIN])

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == RoleEnum.OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove the workspace owner")

    await db.delete(member)
    await db.commit()