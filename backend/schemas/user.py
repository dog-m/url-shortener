import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

#


class UserInfo(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    is_active: bool
    is_superuser: bool
    registered_at: datetime
    updated_at: datetime



class UserUpdate(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    is_active: bool
    is_superuser: bool
    password: str | None = None

