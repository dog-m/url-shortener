from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import require_user
from backend.db.database import get_db_session
from backend.frontend.common import frontend_templates
from backend.models.user import User

#


frontend_user_router = APIRouter(tags=['frontend', 'user'], include_in_schema=False)


@frontend_user_router.api_route('/user', methods=['GET', 'HEAD'])
async def user_main(
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(require_user)] = None,
):
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/main.html',
    )

