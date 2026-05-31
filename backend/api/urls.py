from fastapi import APIRouter
from fastapi.responses import RedirectResponse

#

url_router = APIRouter()


@url_router.get('/u/{id}')
async def visit_url(
    id: str,
    #user: User | None = Depends(get_user),
):
    return RedirectResponse(
        url=f"https://example.com/?u={id}",
        headers={},
    )
