import uuid
from datetime import datetime

from sqlalchemy import JSON, UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#


class ClickEventEntry(BaseDbModel):
    __tablename__ = "clicks"

    id: Mapped[uuid.UUID]       = mapped_column(UUID(), primary_key=True, index=True)
    url_id: Mapped[str]         = mapped_column(ForeignKey('urls.id', ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_UTC, index=True, nullable=False)
    meta: Mapped[int]       = mapped_column(JSON(none_as_null=True), nullable=False)

