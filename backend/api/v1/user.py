from typing import Annotated

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.user import UserInfo

#


api_user_router = APIRouter(prefix='', tags=['api', 'user'])



@api_user_router.get('/user', response_model=UserInfo)
async def user_info(
    user: Annotated[User | None, Depends(get_current_user)] = None,
):
    return user

