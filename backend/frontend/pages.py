from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

#


frontend_router = APIRouter(tags=['frontend'], include_in_schema=False)
frontend_files  = StaticFiles(directory='./frontend', html=False)



@frontend_router.api_route('/index.html', methods=['GET', 'HEAD'])
async def root_explicit(req: Request):
    return await frontend_files.get_response(
        path=req.url.path[1:],
        scope=req.scope,
    )


@frontend_router.api_route('/', methods=['GET', 'HEAD'])
async def root():
    return RedirectResponse('/index.html')



@frontend_router.api_route('/favicon.ico', methods=['GET', 'HEAD'])
async def favicon(req: Request):
    return await frontend_files.get_response(
        path='favicon.png',
        scope=req.scope,
    )



@frontend_router.api_route('/robots.txt', methods=['GET', 'HEAD'])
async def robots(req: Request):
    return await frontend_files.get_response(
        path=req.url.path[1:],
        scope=req.scope,
    )



@frontend_router.api_route('/sitemap.xml', methods=['GET', 'HEAD'])
async def sitemap(req: Request):
    return await frontend_files.get_response(
        path=req.url.path[1:],
        scope=req.scope,
    )



async def not_found_error_handler(req: Request, e: Exception) -> Response:  # noqa: ARG001
    res = await frontend_files.get_response('404.html', req.scope)
    res.status_code = 404
    return res

