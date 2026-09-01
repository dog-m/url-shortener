import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#

USER_EMAIL_MAX_LEN = 255
USER_NAME_MAX_LEN  = 100


class User(BaseDbModel):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID]               = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid1)
    email: Mapped[str]                  = mapped_column(String(USER_EMAIL_MAX_LEN), unique=True, index=True, nullable=False)
    name: Mapped[str]                   = mapped_column(String(USER_NAME_MAX_LEN), index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 'NULL' = 'requires registration'
    is_active: Mapped[bool]             = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool]          = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime]     = mapped_column(DateTime(timezone=True), default=now_UTC, nullable=False)
    updated_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=now_UTC, onupdate=now_UTC, nullable=False)
    version: Mapped[int]                = mapped_column(Integer, nullable=False)

    __mapper_args__ = {
        # enable optimistic locking
        'version_id_col': version,
    }

