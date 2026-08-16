from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_user
from backend.db.database import get_db_session
from backend.frontend.common import frontend_templates
from backend.models.user import User
from backend.services.url import find_url_by_id, find_urls_batched

#


frontend_user_router = APIRouter(tags=['frontend', 'user'], include_in_schema=False)



@frontend_user_router.api_route('/profile', methods=['GET', 'HEAD'])
async def user_profile(
    req: Request,
    user: Annotated[User, Depends(require_user)],
):
    # page rendering (access checks had passed)
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/profile.html',
        media_type='text/html',
        context={
            'user': user,
        }
    )



@frontend_user_router.api_route('/urls', methods=['GET', 'HEAD'])
async def user_url_list(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
    query: Annotated[str, Query(alias='q')] = '',
    page: Annotated[str, Query()] = '0',
    sort: Annotated[str, Query()] = 'updated',
    asc: Annotated[str, Query()] = '0',
):
    # parameter cleanup
    page       = page.strip()
    page_index = max(0, int(page) if page.isnumeric() else 0)
    query      = query[:500].strip()
    sort       = sort.strip().lower()
    asc        = asc.strip()
    page_size  = 50

    # fetch
    urls = await find_urls_batched(
        db,
        owner=user,
        text=query,
        sort_criteria=sort,
        sort_asc=asc != '0',
        batch_size=page_size,
        offset_items=page_index * page_size,
    )

    # page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-list.html',
        media_type='text/html',
        context={
            'user': user,
            'query': query,
            'page': page_index,
            'page_size': page_size,
            'urls': urls,
        }
    )



@frontend_user_router.api_route('/urls/new', methods=['GET', 'HEAD'])
async def user_url_new(
    req: Request,
    user: Annotated[User, Depends(require_user)],
):
    # just page rendering, there is nothing sensitive
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-new.html',
        media_type='text/html',
        context={
            'user': user,
        }
    )



@frontend_user_router.api_route('/urls/{url_id}', methods=['GET', 'HEAD'])
async def user_url_edit(
    req: Request,
    url_id: Annotated[str, Path(min_length=1, max_length=32)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    # parameter validation and access checks
    url = await find_url_by_id(db, url_id)
    if url is None or (url.owner_id != user.id and not user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

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

