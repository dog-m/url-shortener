import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import BaseDbModel, now_UTC

#

CLICK_USER_ADDR_MAX_LEN              = len('[0000:0000:0000:0000:0000:ffff:192.168.100.228]')  # https://stackoverflow.com/a/166157
CLICK_HEADER_USER_AGENT_MAX_LEN      = 256
CLICK_HEADER_REFERER_DOMAIN_MAX_LEN  = 255
CLICK_HEADER_ACCEPT_LANGUAGE_MAX_LEN = 128


class ClickEvent(BaseDbModel):
    __tablename__ = "clicks"

    id: Mapped[uuid.UUID]         = mapped_column(UUID, primary_key=True, index=True)
    url_id: Mapped[str]           = mapped_column(String, ForeignKey('urls.id', ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=now_UTC, index=True, nullable=False)
    user_addr: Mapped[str | None] = mapped_column(String(CLICK_USER_ADDR_MAX_LEN), nullable=True)

    # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
    headers_user_agent: Mapped[str | None] = mapped_column(String(CLICK_HEADER_USER_AGENT_MAX_LEN), nullable=True)

    # "duckduckgo.com"
    headers_referer_domain: Mapped[str | None] = mapped_column(String(CLICK_HEADER_REFERER_DOMAIN_MAX_LEN), nullable=True)

    # "ru,en;q=0.9,en-US;q=0.8"
    headers_accept_language: Mapped[str | None] = mapped_column(String(CLICK_HEADER_ACCEPT_LANGUAGE_MAX_LEN), nullable=True)

