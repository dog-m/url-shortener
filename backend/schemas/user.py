import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr

from backend.validation.name import ValidName

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
    email: EmailStr     = None
    password: SecretStr = None
    name: ValidName     = None



class AdminUpdate(UserUpdate):
    is_active: bool    = None
    is_superuser: bool = None

