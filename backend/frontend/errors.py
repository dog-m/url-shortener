from fastapi import Request, Response

from backend.frontend.common import frontend_files

#



async def not_found_error_handler(req: Request, e: Exception) -> Response:  # noqa: ARG001
    res = await frontend_files.get_response('404.html', req.scope)
    res.status_code = 404
    return res

