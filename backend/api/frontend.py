from fastapi import APIRouter
from fastapi.responses import FileResponse

#

frontend_router = APIRouter(tags=['frontend'])


@frontend_router.get('/', response_class=FileResponse, include_in_schema=False)
async def root():
    return FileResponse(
        './frontend/index.html',
        media_type='text/html',
    )


@frontend_router.get('/favicon.ico', response_class=FileResponse, include_in_schema=False)
async def favicon():
    return FileResponse(
        './frontend/favicon.png',
        media_type='image/png',
    )

