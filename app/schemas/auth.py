from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Annotated

class UserCreate(BaseModel):
    email: Annotated[EmailStr, Field(..., title = "Email", description = "Enter your email address", examples=["examples@gmail.com"])]
    password: Annotated[str, Field(..., title = "Password", description = "Enter your account password")]
    full_name: Annotated[str, Field(..., title = "FullName", description = "Enter your full name as per gov id.", examples = ["Jhon Does"])]


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"