from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from backend.api.dependencies import require_user
from backend.core.security import limiter
from backend.db.database import get_db_session, now_UTC
from backend.models.user import User
from backend.schemas.api_base import ApiOk
from backend.schemas.clicks import ClickActivityStats
from backend.schemas.url import UrlCreate, UrlInfo, UrlUpdate, UrlUpdateResult
from backend.services.clicks import get_click_activity_by_date
from backend.services.url import (
    URL_ID_PATTERN,
    create_new_url,
    find_url_by_id,
    find_urls_batched,
)

#


api_urls_router = APIRouter(prefix='', tags=['url'])



@api_urls_router.get('/urls', response_model=list[UrlInfo])
async def list_urls(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    return await find_urls_batched(db, owner=user)



@api_urls_router.post('/urls', response_model=UrlInfo)
async def add_new_url(
    new_url: Annotated[UrlCreate, Body()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    return await create_new_url(db, user, new_url)



@api_urls_router.patch('/urls/{url_id}', response_model=UrlUpdateResult)
@limiter.limit('1/second')
async def edit_url(
    url_id: Annotated[str, Path(pattern=URL_ID_PATTERN)],
    url_version: Annotated[int, Query(alias='v')],
    patch: Annotated[UrlUpdate, Body()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
    request: Request, response: Response,  # noqa: ARG001 - rate limiting
):
    # validation and access checks
    if (url := await find_url_by_id(db, url_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if url.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # concurrency checks
    if url_version != url.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )

    # apply changes
    try:
        # NOTE: no 'mode=json' here because of datetimes
        for name, value in patch.model_dump(exclude_unset=True).items():
            setattr(url, name, value)

        await db.commit()
    except StaleDataError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )

    return UrlUpdateResult(version=url_version + 1)  # skipping instance refresh



@api_urls_router.delete('/urls/{url_id}', response_model=ApiOk)
async def remove_url(
    url_id: Annotated[str, Path(pattern=URL_ID_PATTERN)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    # validation and access checks
    if (url := await find_url_by_id(db, url_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if url.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # apply the change
    await db.delete(url)
    await db.commit()  # TODO: errors?

    return ApiOk()



@api_urls_router.get('/urls/{url_id}/stats/last-activity', response_model=ClickActivityStats)
async def get_url_stats_last_activity(
    url_id: Annotated[str, Path(pattern=URL_ID_PATTERN)],
    up_to: Annotated[datetime, Query(default_factory=now_UTC)],  # TODO: possible issues with timezones?
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    # validation and access checks
    if (url := await find_url_by_id(db, url_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if url.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # prepare selection criteria
    week_count = 2 * 4  # last two months
    day_count  = 7 * week_count - (7 - (up_to.weekday() + 1)) + 1

    # fetch and return
    return ClickActivityStats(
        dates=await get_click_activity_by_date(db, url.id, up_to, days=day_count),
    )

