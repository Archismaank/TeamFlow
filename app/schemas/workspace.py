from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from app.models.models import RoleEnum


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceOut(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    created_at: datetime
    role: RoleEnum | None = None

    model_config = {"from_attributes": True}


class MemberInvite(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.MEMBER


class MemberRoleUpdate(BaseModel):
    role: RoleEnum


class WorkspaceMemberOut(BaseModel):
    user_id: UUID
    full_name: str
    email: EmailStr
    role: RoleEnum

    model_config = {"from_attributes": True}