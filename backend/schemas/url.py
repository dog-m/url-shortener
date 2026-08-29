from datetime import datetime

from pydantic import BaseModel, HttpUrl

#


class UrlInfo(BaseModel):
    id: str
    original_url: str
    is_active: bool
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None



class UrlCreate(BaseModel):
    original_url: HttpUrl
    is_active: bool = True
    title: str
    description: str | None = None



class UrlUpdate(BaseModel):
    id: str
    original_url: HttpUrl
    is_active: bool
    title: str
    description: str | None = None

