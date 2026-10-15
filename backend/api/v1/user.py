from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Path,
    Query,
    Request,
    Response,
)

from backend.api.dependencies import require_admin, require_user
from backend.core.security import limiter
from backend.models.user import User
from backend.schemas.api_base import ApiOk
from backend.schemas.user import UserInfo, UserUpdate
from backend.services.user import UserService

#


router = APIRouter(prefix='', tags=['user'])



@router.get('/me', response_model=UserInfo)
async def get_current_user_profile(
    user: Annotated[User, Depends(require_user)],
) -> object:
    return user



@router.patch('/me', response_model=ApiOk)
@limiter.limit('1/second')
async def edit_current_user_profile(
    version: Annotated[int, Query(alias='v')],
    patch: Annotated[UserUpdate, Body()],
    user_service: Annotated[UserService, Depends()],
    user: Annotated[User, Depends(require_user)],
    request: Request, response: Response,  # noqa: ARG001 - rate limiting
) -> object:
    await user_service.update_user_profile(user, patch, version)
    return ApiOk()



@router.patch('/user/{user_id}', response_model=ApiOk)
@limiter.limit('1/second')
async def edit_user_profile(
    user_id: Annotated[UUID, Path()],
    version: Annotated[int, Query(alias='v')],
    patch: Annotated[UserUpdate, Body()],
    user_service: Annotated[UserService, Depends()],
    admin: Annotated[User, Depends(require_admin)],  # noqa: ARG001 - privileged action
    request: Request, response: Response,  # noqa: ARG001 - rate limiting
) -> object:
    user = await user_service.get_user_by_id(user_id)
    await user_service.update_user_profile(user, patch, version)
    return ApiOk()

