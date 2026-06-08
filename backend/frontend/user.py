from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db_session
from backend.frontend.common import frontend_files

#


frontend_user_router = APIRouter(tags=['frontend', 'user'], include_in_schema=False)


@frontend_user_router.api_route('/user', methods=['GET', 'HEAD'])
async def user_main(
    req: Request,
    session: AsyncSession = Depends(get_db_session),
):
    return await frontend_files.get_response(
        path='user.html',
        scope=req.scope,
    )

