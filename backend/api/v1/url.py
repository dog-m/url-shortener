from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_user
from backend.db.database import get_db_session
from backend.models.user import User
from backend.schemas.url import UrlCreate, UrlInfo, UrlUpdate
from backend.services.url import (
    create_new_url,
    find_url_by_id,
    find_urls_batched,
    update_url,
)

#


api_urls_router = APIRouter(prefix='', tags=['api', 'user'])



@api_urls_router.get('/urls', response_model=list[UrlInfo])
async def list_urls(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    return await find_urls_batched(db, owner=user)



@api_urls_router.post('/urls', response_model=UrlInfo)
async def add_new_url(
    new_url: Annotated[UrlCreate, Body()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    return await create_new_url(db, user, new_url)



@api_urls_router.patch('/urls')
async def edit_url(
    url_patch: Annotated[UrlUpdate, Body()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)],
):
    url = await find_url_by_id(db, url_patch.id, lock=True)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if url.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # patch
    url_patch.original_url = str(url_patch.original_url)

    await update_url(db, url_patch)
    return {
        'status': 'ok',
    }

