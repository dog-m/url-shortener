from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_admin
from backend.db.database import get_db_session
from backend.frontend.common import frontend_templates
from backend.models.user import User
from backend.services.user import get_all_users_batched

#


frontend_admin_router = APIRouter(tags=['frontend', 'user'], include_in_schema=False)


@frontend_admin_router.api_route('/users', methods=['GET', 'HEAD'])
async def admin_user_list(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_admin)],
    page: Annotated[str, Query()] = '0',
):
    # silent query parameter filtering
    page_index = int(page) if page.isnumeric() else 0
    page_index = max(0, page_index)

    page_size = 50

    return frontend_templates.TemplateResponse(
        request=req,
        name='admin/user-list.html',
        media_type='text/html',
        context={
            'user': user,
            'users': get_all_users_batched(db, offset=page_index * page_size, batch_size=page_size),
            'page': page_index,
        }
    )



@frontend_admin_router.api_route('/user/{user_id}/profile', methods=['GET', 'HEAD'])
async def admin_user_profile(
    req: Request,
    user_id: Annotated[str, Path()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_admin)],
):
    return frontend_templates.TemplateResponse(
        request=req,
        name='admin/user-profile-edit.html',
        media_type='text/html',
        context={
            'user': user,
        }
    )


@frontend_admin_router.api_route('/user/{user_id}/urls', methods=['GET', 'HEAD'])
async def admin_user_url_list(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_admin)],
    search: Annotated[str, Query()] = '',
    page: Annotated[str, Query()] = '0',
):
    # silent query parameter filtering
    page_index = int(page) if page.isnumeric() else 0
    page_index = max(0, page_index)
    search = search[:500].strip()

    return frontend_templates.TemplateResponse(
        request=req,
        name='admin/user-url-list.html',  # ???
        media_type='text/html',
        context={
            'user': user,
            'search': search,
            'page': page_index,
        }
    )
