from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from backend.frontend.common import frontend_files

#

frontend_index_router = APIRouter(tags=['frontend', 'SEO'], include_in_schema=False)


@frontend_index_router.api_route('/index.html', methods=['GET', 'HEAD'])
async def root_explicit():
    return RedirectResponse('/')


@frontend_index_router.api_route('/', methods=['GET', 'HEAD'])
async def root(req: Request):
    return await frontend_files.get_response(
        path='index.html',
        scope=req.scope,
    )


@frontend_index_router.api_route('/favicon.ico', methods=['GET', 'HEAD'])
async def favicon(req: Request):
    return await frontend_files.get_response(
        path='favicon.png',
        scope=req.scope,
    )

