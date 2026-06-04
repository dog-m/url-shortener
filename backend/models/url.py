from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#

URL_ID_MAX_LEN          = 10
URL_TITLE_MAX_LEN       = 255
URL_DESCRIPTION_MAX_LEN = 512


class UrlDto(BaseDbModel):
    __tablename__ = "urls"

    id: Mapped[str]                     = mapped_column(String(URL_ID_MAX_LEN), primary_key=True, index=True)
    original_url: Mapped[str]           = mapped_column(String(2048), nullable=False)
    is_active: Mapped[bool]             = mapped_column(Boolean, default=True)
    title: Mapped[str | None]           = mapped_column(String(URL_TITLE_MAX_LEN), nullable=True)
    description: Mapped[str | None]     = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=now_UTC, nullable=False)
    updated_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=now_UTC, onupdate=now_UTC, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[int]               = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

