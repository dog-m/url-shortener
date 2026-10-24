from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Request,
    Response,
)
from fastapi.responses import HTMLResponse

from backend.api.dependencies import require_user
from backend.db.database import now_UTC
from backend.frontend.common import frontend_templates
from backend.models.user import User
from backend.services.exceptions import UrlNotFoundError
from backend.services.url import UrlCategory, UrlService

#


router = APIRouter(prefix='/urls', tags=['urls'])



@router.get('', response_class=HTMLResponse)
async def url_search(
    req: Request,
    url_service: Annotated[UrlService, Depends()],
    user: Annotated[User, Depends(require_user)],
    query: Annotated[str, Query(alias='q')] = '',
    page: Annotated[str, Query(alias='p')] = '1',  # using "natural" numbers instead of zero-based indexing
    sort: Annotated[str, Query()] = 'updated',
    asc: Annotated[str, Query()] = 'off',
    category: Annotated[str, Query(alias='c')] = '',
    user_id: Annotated[UUID | None, Query(min_length=1, max_length=38)] = None,  # MS GUID format
) -> Response:
    # parameter cleanup
    page         = page.strip()
    page_index   = int(page) if page.isnumeric() else 0
    query        = query[:500].strip()
    sort         = sort.strip().lower()
    sort_asc     = asc == 'on'
    now_utc      = now_UTC().replace(tzinfo=None)
    url_category = UrlCategory(category) if category else None
    page_size    = 20

    # access checks
    owner = user_id if user_id and user.is_superuser else user

    # fetch
    if page_index > 0:
        urls = await url_service.find_urls_batched(
            text=query,
            owner=owner,
            sort_criteria=sort,
            sort_asc=sort_asc,
            batch_size=page_size,
            offset_items=(page_index - 1) * page_size,
            url_category=url_category,
            now_utc=now_utc,
        )
    else:
        urls = []

    # page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-list.html',
        media_type='text/html',
        context={
            'user': user,
            'page': page_index,
            'page_size': page_size,
            'urls': urls,
            'now_UTC': now_UTC().replace(tzinfo=None),
            'query': query,
            'sort': sort,
            'sort_asc': sort_asc,
            'category': category,
        }
    )



@router.get('/new', response_class=HTMLResponse)
async def url_new(
    req: Request,
    user: Annotated[User, Depends(require_user)],
) -> Response:
    # just page rendering, there is nothing sensitive
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-new.html',
        media_type='text/html',
        context={
            'user': user,
        }
    )



@router.get('/{url_id}/overview', response_class=HTMLResponse)
async def url_overview(
    req: Request,
    url_id: Annotated[str, Path()],
    url_service: Annotated[UrlService, Depends()],
    user: Annotated[User, Depends(require_user)],
) -> Response:
    # parameter validation and access checks
    url = await url_service.get_url_by_id(url_id)
    if url.owner_id != user.id and not user.is_superuser:
        raise UrlNotFoundError(url_id)

    # page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-overview.html',
        media_type='text/html',
        context={
            'user': user,
            'url': url,
            'now_UTC': now_UTC().replace(tzinfo=None),
        }
    )



@router.get('/{url_id}/edit', response_class=HTMLResponse)
async def url_edit(
    req: Request,
    url_id: Annotated[str, Path()],
    url_service: Annotated[UrlService, Depends()],
    user: Annotated[User, Depends(require_user)],
) -> Response:
    # parameter validation and access checks
    url = await url_service.get_url_by_id(url_id)
    if url.owner_id != user.id and not user.is_superuser:
        raise UrlNotFoundError(url_id)

    # page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-edit.html',
        media_type='text/html',
        context={
            'user': user,
            'url': url,
        }
    )

