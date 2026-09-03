from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from backend.api.dependencies import require_user
from backend.core.security import limiter, password_get_hash
from backend.db.database import get_db_session
from backend.models.user import User
from backend.schemas.api_base import ApiOk
from backend.schemas.user import UserInfo, UserUpdate

#


api_user_router = APIRouter(prefix='', tags=['user'])



@api_user_router.get('/me', response_model=UserInfo)
async def get_current_user_profile(
    user: Annotated[User, Depends(require_user)],
):
    return user



@api_user_router.patch('/user/{user_id}', response_model=ApiOk)
@limiter.limit('1/second')
async def edit_user_profile(
    user_id: Annotated[str, Path()],
    user_version: Annotated[int, Query(alias='v')],
    patch: Annotated[UserUpdate, Body()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
):
    # access checks
    if user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # concurrency checks
    if user_version != user.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )

    # in-place corrections
    patch_data = patch.model_dump(mode='json', exclude_unset=True)
    if pwd := patch_data.get('password'):
        del patch_data['password']
        patch_data['hashed_password'] = password_get_hash(pwd)

    # apply changes
    try:
        for name, value in patch_data.items():
            setattr(user, name, value)

        await db.commit()
    except StaleDataError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )

    return ApiOk()

