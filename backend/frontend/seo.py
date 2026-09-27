from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse

from backend.frontend.common import frontend_files

#


router = APIRouter(tags=['frontend', 'SEO'])


@router.api_route('/robots.txt', methods=['GET', 'HEAD'], response_class=FileResponse)
async def robots(req: Request) -> Response:
    return await frontend_files.get_response(
        path=req.url.path[1:],
        scope=req.scope,
    )


@router.api_route('/sitemap.xml', methods=['GET', 'HEAD'], response_class=FileResponse)
async def sitemap(req: Request) -> Response:
    return await frontend_files.get_response(
        path=req.url.path[1:],
        scope=req.scope,
    )

