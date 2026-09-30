from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_admin
from backend.db.database import get_db_session
from backend.frontend.common import frontend_templates
from backend.models.user import User
from backend.services.user import find_users_batched, get_user_by_id

#


router = APIRouter(tags=['admin'])



@router.get('/users', response_class=HTMLResponse)
async def get_user_list(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    admin: Annotated[User, Depends(require_admin)],
    page: Annotated[str, Query()] = '1',
) -> Response:
    # parameter cleanup
    page       = page.strip()
    page_index = int(page) if page.isnumeric() else 1
    page_size  = 50

    # fetch
    if page_index > 0:
        users = await find_users_batched(
            db,
            batch_size=page_size,
            offset_items=(page_index - 1) * page_size,
        )
    else:
        users = []

    # page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='admin/user-list.html',
        media_type='text/html',
        context={
            'user': admin,  # pages/tabs jinja logic relies on 'user' being present
            'page': page_index,
            'page_size': page_size,
            'users': users,
        }
    )



@router.get('/users/{user_id}/profile', response_class=HTMLResponse)
async def get_user_profile(
    req: Request,
    user_id: Annotated[UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    admin: Annotated[User, Depends(require_admin)],
) -> Response:
    # validation
    if (profile := await get_user_by_id(db, user_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # conveniences
    if user_id == admin.id:
        return RedirectResponse(
            url='/profile',
        )

    # just page rendering
    return frontend_templates.TemplateResponse(
        request=req,
        name='admin/user-profile-edit.html',
        media_type='text/html',
        context={
            'user': admin,  # pages/tabs jinja logic relies on 'user' being present
            'profile': profile,
        }
    )

