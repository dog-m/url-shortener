from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, RedirectResponse

from backend.frontend.common import frontend_files

#

router = APIRouter(tags=['frontend', 'SEO'])


@router.api_route('/index.html', methods=['GET', 'HEAD'], response_class=RedirectResponse)
async def root_explicit() -> Response:
    return RedirectResponse('/')


@router.api_route('/', methods=['GET', 'HEAD'], response_class=FileResponse)
async def root(req: Request) -> Response:
    return await frontend_files.get_response(
        path='index.html',
        scope=req.scope,
    )


@router.api_route('/favicon.ico', methods=['GET', 'HEAD'], response_class=FileResponse)
async def favicon(req: Request) -> Response:
    return await frontend_files.get_response(
        path='favicon.png',
        scope=req.scope,
    )

