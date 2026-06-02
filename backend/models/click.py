import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#

HEADER_USER_AGENT_MAX_LEN      = 256
HEADER_REFERER_DOMAIN_MAX_LEN  = 255
HEADER_ACCEPT_LANGUAGE_MAX_LEN = 128


class ClickEventEntry(BaseDbModel):
    __tablename__ = "clicks"

    id: Mapped[uuid.UUID]       = mapped_column(UUID, primary_key=True, index=True)
    url_id: Mapped[str]         = mapped_column(ForeignKey('urls.id', ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_UTC, index=True, nullable=False)

    # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
    headers_user_agent: Mapped[str | None] = mapped_column(String(HEADER_USER_AGENT_MAX_LEN), nullable=True)

    # "duckduckgo.com"
    headers_referer_domain: Mapped[str | None] = mapped_column(String(HEADER_REFERER_DOMAIN_MAX_LEN), nullable=True)

    # "ru,en;q=0.9,en-US;q=0.8"
    headers_accept_language: Mapped[str | None] = mapped_column(String(HEADER_ACCEPT_LANGUAGE_MAX_LEN), nullable=True)

