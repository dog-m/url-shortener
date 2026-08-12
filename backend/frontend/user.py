from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_user
from backend.db.database import get_db_session
from backend.frontend.common import frontend_templates
from backend.models.user import User

#


frontend_user_router = APIRouter(tags=['frontend', 'user'], include_in_schema=False)


@frontend_user_router.api_route('/profile', methods=['GET', 'HEAD'])
async def user_profile(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
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
    search: Annotated[str, Query()] = '',
    page: Annotated[str, Query()] = '0',
):
    # silent query parameter filtering
    page_index = int(page) if page.isnumeric() else 0
    page_index = max(0, page_index)
    search = search[:500].strip()

    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-list.html',
        media_type='text/html',
        context={
            'user': user,
            'search': search,
            'page': page_index,
        }
    )



@frontend_user_router.api_route('/urls/new', methods=['GET', 'HEAD'])
async def user_url_new(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
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
    url_id: Annotated[str, Path(min_length=1)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/url-edit.html',
        media_type='text/html',
        context={
            'user': user,
            'url': url_id,
        }
    )

