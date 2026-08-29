from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from backend.api.dependencies import require_user
from backend.models.user import User
from backend.schemas.api_base import ApiOk
from backend.schemas.user import UserInfo, UserUpdate

#


api_user_router = APIRouter(prefix='', tags=['api', 'user'])



@api_user_router.get('/user', response_model=UserInfo)
async def user_info(
    user: Annotated[User, Depends(require_user)],
):
    return user



@api_user_router.patch('/user', response_model=ApiOk)
async def update_user(
    patch: Annotated[UserUpdate, Body()],
    user: Annotated[User, Depends(require_user)],
):
    # validation and access checks
    if patch.id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Changing someone else's profile is not allowed",
        )

    print('[!!!]', patch)

    return ApiOk()

