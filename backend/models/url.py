from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#


class URL(BaseDbModel):
    __tablename__ = "urls"

    id: Mapped[str]                           = mapped_column(String(10), primary_key=True, index=True)
    original_url: Mapped[str]                 = mapped_column(String(2048), nullable=False)
    is_active: Mapped[bool]                   = mapped_column(Boolean, default=True)
    title: Mapped[str | None]                 = mapped_column(String(255), nullable=True)
    description: Mapped[str | None]           = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]              = mapped_column(DateTime(timezone=True), default=now_UTC, nullable=False)
    updated_at: Mapped[datetime]              = mapped_column(DateTime(timezone=True), default=now_UTC, onupdate=now_UTC, nullable=False)
    expires_at: Mapped[datetime | None]       = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[int]                     = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

