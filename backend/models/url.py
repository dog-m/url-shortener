import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#

URL_TITLE_MAX_LEN       = 255
URL_DESCRIPTION_MAX_LEN = 512


class Url(BaseDbModel):
    __tablename__ = 'urls'

    id: Mapped[str]                     = mapped_column(String(100), primary_key=True, index=True)
    original_url: Mapped[str]           = mapped_column(String(2048), nullable=False)
    is_active: Mapped[bool]             = mapped_column(Boolean, default=True)
    title: Mapped[str]                  = mapped_column(String(URL_TITLE_MAX_LEN), nullable=False)
    description: Mapped[str]            = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=now_UTC, nullable=False)
    updated_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=now_UTC, onupdate=now_UTC, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[uuid.UUID]         = mapped_column(UUID, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    version: Mapped[int]                = mapped_column(Integer, nullable=False)

    __mapper_args__ = {
        # enable optimistic locking
        'version_id_col': version,
    }

