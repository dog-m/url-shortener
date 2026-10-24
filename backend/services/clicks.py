import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy import func, select

from backend.db.extensions import UniversalWeekday
from backend.models.click import ClickEvent, UrlVisitorMetadata
from backend.schemas.clicks import (
    WEEKDAY_INDEX_TO_ATTR_NAME,
    ClickActivityDaily,
    ClickActivityWeekly,
)
from backend.services.base import BaseService

#

logger = logging.getLogger(__name__)


class ClicksService(BaseService):

    async def get_click_activity_by_date(self, url_id: str, now: datetime, *, days: int = 30) -> list[ClickActivityDaily]:
        assert days > 0

        # fetch the data
        day_col = func.date(ClickEvent.timestamp).label('day')
        stmt = (
            select(
                day_col,
                func.count(ClickEvent.id).label('count')
            )
            .where(ClickEvent.url_id == url_id)
            .where(ClickEvent.timestamp >= (now - timedelta(days=days)))
            .group_by(day_col)
        )

        rows = await self.db.execute(stmt)
        click_map = {
            row.day: int(row.count)  # type: ignore  # possible format mismatch issue here?
            for row in rows.all()
        }

        # fill-in the gaps (days without clicks)
        result: list[ClickActivityDaily] = []
        for i in range(days):
            day = (now - timedelta(days=i)).date()
            day_str = day.isoformat()  # possible format mismatch issue here?
            entry = ClickActivityDaily(
                date=day_str,
                count=click_map.get(day_str, 0),
            )
            result.append(entry)

        # order things manually lowering strain on the DB
        result.sort(key=lambda x: x.date)

        return result


    async def get_click_activity_by_weekday(self, url_id: str, now: datetime, *, days: int = 30) -> ClickActivityWeekly:
        assert days > 0

        # fetch the data
        weekday_col = UniversalWeekday(ClickEvent.timestamp).label('weekday_num')
        stmt = (
            select(
                weekday_col,
                func.count(ClickEvent.id).label('count')
            )
            .where(ClickEvent.url_id == url_id)
            .where(ClickEvent.timestamp >= (now - timedelta(days=days)))
            .group_by(weekday_col)
        )
        rows = await self.db.execute(stmt)

        # fill-in the days
        result = ClickActivityWeekly()
        for row in rows.all():
            day_name = WEEKDAY_INDEX_TO_ATTR_NAME[int(row.weekday_num)]
            setattr(result, day_name, row.count)

        return result


    async def register_url_visit(self, url_id: str, visitor: UrlVisitorMetadata) -> None:
        click = ClickEvent(
            id=uuid.uuid1(),  # FIXME: use UUID7 on later Python versions
            url_id=url_id,
            user_addr=visitor.ip,
            headers_user_agent=visitor.headers_user_agent,
            headers_referer_domain=visitor.headers_referer_domain,
            headers_accept_language=visitor.headers_accept_language,
        )
        self.db.add(click)
        await self.db.commit()
        # TODO: batch insertion?

