from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from backend.api.dependencies import require_user
from backend.frontend.common import frontend_templates
from backend.models.user import User

#


frontend_user_router = APIRouter(tags=['user'])



@frontend_user_router.api_route('/profile', methods=['GET', 'HEAD'], response_class=HTMLResponse)
async def user_profile(
    req: Request,
    user: Annotated[User, Depends(require_user)],
):
    # page rendering (access checks had passed)
    return frontend_templates.TemplateResponse(
        request=req,
        name='user/profile.html',
        media_type='text/html',
        context={
            'user': user,
        }
    )

