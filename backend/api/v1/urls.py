from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from backend.api.dependencies import get_current_user
from backend.models.user import User

#


api_urls_router = APIRouter(prefix='', tags=['api', 'urls'])


@api_urls_router.get('/u/{id}')
async def visit_url(
    id: str,
    req: Request,
    user: Annotated[User | None, Depends(get_current_user)] = None,
):
    ip = '0.0.0.0'
    if (addr := req.client) is not None:
        ip = addr.host

    print('[~~~] user =', user.id if user else None)

    return RedirectResponse(
        url=f"https://example.com/?u={id},ip={ip}",
        headers={},
    )
