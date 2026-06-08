from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

#


api_urls_router = APIRouter(prefix='', tags=['api', 'urls'])


@api_urls_router.get('/u/{id}')
async def visit_url(
    id: str,
    #user: User | None = Depends(get_user),
    req: Request,
):
    ip = '0.0.0.0'
    if (addr := req.client) is not None:
        ip = addr.host

    return RedirectResponse(
        url=f"https://example.com/?u={id},ip={ip}",
        headers={},
    )
