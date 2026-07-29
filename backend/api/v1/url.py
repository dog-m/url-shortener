from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_user
from backend.db.database import get_db_session
from backend.models.user import User
from backend.schemas.url import UrlCreate, UrlInfo
from backend.services.url import create_new_url, list_user_urls

#


api_urls_router = APIRouter(prefix='', tags=['api', 'user'])



@api_urls_router.get('/urls', response_model=list[UrlInfo])
async def user_urls(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    return await list_user_urls(db, user)



@api_urls_router.post('/urls', response_model=UrlInfo)
async def user_urls_add(
    new_url: Annotated[UrlCreate, Body()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    return await create_new_url(db, user, new_url)

