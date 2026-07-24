from datetime import datetime

from pydantic import BaseModel

#


class UrlInfo(BaseModel):
    id: str
    original_url: str
    is_active: bool
    title: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None



class UrlCreate(BaseModel):
    original_url: str
    title: str | None = None
    description: str | None = None

