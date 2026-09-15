import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.extensions import UniversalWeekday
from backend.models.click import ClickEvent
from backend.schemas.clicks import (
    WEEKDAY_INDEX_TO_ATTR_NAME,
    ClickActivityDaily,
    ClickActivityWeekly,
)

#

logger = logging.getLogger(__name__)



async def get_click_activity_by_date(db: AsyncSession, now: datetime, *, days: int = 30) -> list[ClickActivityDaily]:
    assert days > 0

    # fetch the data
    day_column = func.date(ClickEvent.timestamp).label('day')
    stmt = (
        select(
            day_column,
            func.count(ClickEvent.id).label('count')
        )
        .where(ClickEvent.timestamp >= (now - timedelta(days=days)))
        .group_by(day_column)
        .order_by(day_column)
    )

    rows = await db.execute(stmt)
    click_map = {
        row.day: int(row.count)  # possible format mismatch issue here?
        for row in rows.all()
    }

    # fill-in the gaps (days without clicks)
    result = []
    for i in range(days):
        day = (now - timedelta(days=i)).date()
        day_str = day.isoformat()  # possible format mismatch issue here?
        entry = ClickActivityDaily(
            date=day_str,
            count=click_map.get(day_str, 0),
        )
        result.append(entry)

    return result



async def get_click_activity_by_weekday(db: AsyncSession, now: datetime, *, days: int = 30) -> ClickActivityWeekly:
    assert days > 0

    # fetch the data
    weekday_expr = UniversalWeekday(ClickEvent.timestamp).label('weekday_num')
    stmt = (
        select(
            weekday_expr,
            func.count(ClickEvent.id).label('count')
        )
        .where(ClickEvent.timestamp >= (now - timedelta(days=days)))
        .group_by(weekday_expr)
        .order_by(weekday_expr)
    )
    rows = await db.execute(stmt)

    # fill-in the gaps (days without clicks)
    result = ClickActivityWeekly()
    for row in rows.all():
        day_name = WEEKDAY_INDEX_TO_ATTR_NAME[int(row.weekday_num)]
        setattr(result, day_name, row.count)

    return result

