from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    FieldSerializationInfo,
    HttpUrl,
    StringConstraints,
    field_serializer,
)

#


class UrlInfo(BaseModel):
    id: str
    original_url: str
    is_active: bool
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None



class UrlCreate(BaseModel):
    original_url: HttpUrl
    is_active: bool             = True
    title: str
    description: str
    expires_at: datetime | None = None

    @field_serializer('original_url')
    def ser_url(self, value, info: FieldSerializationInfo):
        return str(value)



class UrlUpdate(BaseModel):
    original_url: HttpUrl       = None
    is_active: bool             = None
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] = None
    description: str            = None
    expires_at: datetime | None = None

    @field_serializer('original_url')
    def ser_url(self, value, info: FieldSerializationInfo):
        return str(value)



class UrlUpdateResult(BaseModel):
    version: int

