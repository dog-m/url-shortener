import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel

#


SESSION_ID_MAX_LEN = 64


class Session(BaseDbModel):
    __tablename__ = "sessions"

    id: Mapped[str]              = mapped_column(String(SESSION_ID_MAX_LEN), primary_key=True, nullable=False)
    user_id: Mapped[uuid.UUID]   = mapped_column(UUID, ForeignKey('urls.id', ondelete="CASCADE"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

