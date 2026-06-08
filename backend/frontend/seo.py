from fastapi import APIRouter, Request

from backend.frontend.common import frontend_files

#


frontend_seo_router = APIRouter(tags=['frontend', 'SEO'], include_in_schema=False)


@frontend_seo_router.api_route('/robots.txt', methods=['GET', 'HEAD'])
async def robots(req: Request):
    return await frontend_files.get_response(
        path=req.url.path[1:],
        scope=req.scope,
    )


@frontend_seo_router.api_route('/sitemap.xml', methods=['GET', 'HEAD'])
async def sitemap(req: Request):
    return await frontend_files.get_response(
        path=req.url.path[1:],
        scope=req.scope,
    )

