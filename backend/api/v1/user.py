from typing import Annotated

from fastapi import APIRouter, Depends, Form

from backend.api.dependencies import require_user
from backend.models.user import User
from backend.schemas.user import UserInfo, UserUpdate

#


api_user_router = APIRouter(prefix='', tags=['api', 'user'])



@api_user_router.get('/user', response_model=UserInfo)
async def user_info(
    user: Annotated[User, Depends(require_user)],
):
    return user



@api_user_router.post('/user')
async def update_user(
    new_info: Annotated[UserUpdate, Form(...)],
    user: Annotated[User, Depends(require_user)],
):
    if new_info.password and '\n' in new_info.password:  # check placeholder value
        new_info.password = None

    print('[!!!]', new_info)

    return {}
