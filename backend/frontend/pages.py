from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, RedirectResponse

#

frontend_router = APIRouter(tags=['frontend'])



@frontend_router.get('/', response_class=FileResponse, include_in_schema=False)
async def root():
    return FileResponse(
        './frontend/index.html',
        media_type='text/html',
    )



@frontend_router.get('/index.html', response_class=RedirectResponse, include_in_schema=False)
async def root_alt():
    return RedirectResponse('/')



@frontend_router.get('/favicon.ico', response_class=FileResponse, include_in_schema=False)
async def favicon():
    return FileResponse(
        './frontend/favicon.png',
        media_type='image/png',
    )



@frontend_router.get('/robots.txt', response_class=FileResponse, include_in_schema=False)
async def robots():
    return FileResponse(
        './frontend/robots.txt',
        media_type='text/plain',
    )



@frontend_router.get('/sitemap.xml', response_class=FileResponse, include_in_schema=False)
async def sitemap():
    return FileResponse(
        './frontend/sitemap.xml',
        media_type='text/xml',
    )



async def not_found_error_handler(req: Request, e: Exception) -> Response:  # noqa: ARG001
    return FileResponse(
        './frontend/404.html',
        status_code=404,
        headers={},
        media_type='text/html',
    )
