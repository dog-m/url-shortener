from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Path,
    Query,
    Request,
    Response,
)

from backend.api.dependencies import require_user
from backend.core.security import limiter
from backend.db.database import now_UTC
from backend.models.user import User
from backend.schemas.api_base import ApiOk
from backend.schemas.clicks import ClickActivityStats
from backend.schemas.url import UrlCreate, UrlInfo, UrlUpdate, UrlUpdateResult
from backend.services.clicks import ClicksService
from backend.services.security import SecurityService
from backend.services.url import URL_ID_PATTERN, UrlService

#


router = APIRouter(prefix='/urls', tags=['url'])



@router.get('', response_model=list[UrlInfo])
async def list_urls(
    url_service: Annotated[UrlService, Depends()],
    user: Annotated[User, Depends(require_user)],
) -> object:
    return await url_service.find_urls_batched(owner=user)



@router.post('', response_model=UrlInfo)
async def add_new_url(
    new_url: Annotated[UrlCreate, Body()],
    owner: Annotated[User, Depends(require_user)],
    url_service: Annotated[UrlService, Depends()],
) -> object:
    return await url_service.create_new_url(owner, new_url)



@router.patch('/{url_id}', response_model=UrlUpdateResult)
@limiter.limit('1/second')
async def edit_url(
    url_id: Annotated[str, Path(pattern=URL_ID_PATTERN)],
    url_version: Annotated[int, Query(alias='v')],
    patch: Annotated[UrlUpdate, Body()],
    user: Annotated[User, Depends(require_user)],
    url_service: Annotated[UrlService, Depends()],
    security_service: Annotated[SecurityService, Depends()],
    request: Request, response: Response,  # noqa: ARG001 - rate limiting
) -> object:
    url = await url_service.get_url_by_id(url_id)
    await security_service.can_manage_url(user, url)
    new_version = await url_service.update_url(url, patch, url_version)
    return UrlUpdateResult(version=new_version)



@router.delete('/{url_id}', response_model=ApiOk)
async def remove_url(
    url_id: Annotated[str, Path(pattern=URL_ID_PATTERN)],
    user: Annotated[User, Depends(require_user)],
    url_service: Annotated[UrlService, Depends()],
    security_service: Annotated[SecurityService, Depends()],
) -> object:
    # validation and access checks
    url = await url_service.get_url_by_id(url_id)
    await security_service.can_manage_url(user, url)
    await url_service.delete_url(url)
    return ApiOk()



@router.get('/{url_id}/stats/last-activity', response_model=ClickActivityStats)
async def get_url_stats_last_activity(
    url_id: Annotated[str, Path(pattern=URL_ID_PATTERN)],
    up_to: Annotated[datetime, Query(default_factory=now_UTC)],  # TODO: possible issues with timezones?
    user: Annotated[User, Depends(require_user)],
    url_service: Annotated[UrlService, Depends()],
    security_service: Annotated[SecurityService, Depends()],
    clicks_service: Annotated[ClicksService, Depends()],
) -> object:
    # validation and access checks
    url = await url_service.get_url_by_id(url_id)
    await security_service.can_manage_url(user, url)

    # prepare selection criteria
    week_count = 2 * 4  # last two months
    day_count  = 7 * week_count - (7 - (up_to.weekday() + 1)) + 1

    # fetch and return
    return await clicks_service.get_click_activity_by_date(url.id, up_to, days=day_count)

