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

from backend.api.dependencies import require_admin
from backend.frontend.common import frontend_templates
from backend.models.user import User
from backend.services.user import UserService

#


router = APIRouter(tags=['admin'])



@router.get('/users', response_class=HTMLResponse)
async def get_user_list(
    req: Request,
    admin: Annotated[User, Depends(require_admin)],
    user_service: Annotated[UserService, Depends()],
    page: Annotated[str, Query()] = '1',
) -> Response:
    # parameter cleanup
    page       = page.strip()
    page_index = int(page) if page.isnumeric() else 1
    page_size  = 50

    # fetch
    if page_index > 0:
        users = await user_service.find_users_batched(
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
    admin: Annotated[User, Depends(require_admin)],
    user_service: Annotated[UserService, Depends()],
) -> Response:
    # validation
    if (profile := await user_service.find_user_by_id(user_id)) is None:
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

