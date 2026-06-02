import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#

USER_EMAIL_MAX_LEN = 255
USER_NAME_MAX_LEN  = 100


class UserEntry(BaseDbModel):
    __tablename__ = "users"

    id: Mapped[uuid.UUID]           = mapped_column(UUID, primary_key=True, index=True)
    email: Mapped[str]              = mapped_column(String(USER_EMAIL_MAX_LEN), unique=True, index=True, nullable=False)
    name: Mapped[str]               = mapped_column(String(USER_NAME_MAX_LEN), index=True, nullable=False)
    hashed_password: Mapped[str]    = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool]         = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool]      = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_UTC, nullable=False)
    updated_at: Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=now_UTC, onupdate=now_UTC, nullable=False)
