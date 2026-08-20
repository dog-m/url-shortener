from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_admin
from backend.db.database import get_db_session
from backend.frontend.common import frontend_templates
from backend.models.user import User
from backend.services.user import get_all_users_batched, get_user_by_id

#


frontend_admin_router = APIRouter(tags=['admin'])



@frontend_admin_router.api_route('/users', methods=['GET', 'HEAD'], response_class=HTMLResponse)
async def admin_user_list(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_admin)],
    page: Annotated[str, Query()] = '0',
):
    # parameter cleanup
    page       = page.strip()
    page_index = max(0, int(page) if page.isnumeric() else 0)
    page_size  = 50

    # fetch
    users = await get_all_users_batched(
        db,
        batch_size=page_size,
        offset_items=page_index * page_size,
    )

    # page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='admin/user-list.html',
        media_type='text/html',
        context={
            'user': user,
            'page': page_index,
            'users': users,
        }
    )



@frontend_admin_router.api_route('/user/{user_id}/profile', methods=['GET', 'HEAD'], response_class=HTMLResponse)
async def admin_user_profile(
    req: Request,
    user_id: Annotated[str, Path(min_length=1, max_length=38)],  # MS GUID format
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_admin)],
):
    # validation
    profile = await get_user_by_id(db, user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # just page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='admin/user-profile-edit.html',
        media_type='text/html',
        context={
            'user': user,
            'profile': profile,
        }
    )

