from typing import Annotated
from urllib.parse import urlencode, urlsplit

from fastapi import APIRouter, Depends, Path, Request, Response, status
from fastapi.responses import RedirectResponse

from backend.api.dependencies import (
    get_current_session,
    get_current_session_id,
    get_current_user,
)
from backend.models.click import UrlVisitorMetadata
from backend.services.auth import AuthService
from backend.services.clicks import ClicksService
from backend.services.exceptions import UrlNotFoundError
from backend.services.security import SecurityService
from backend.services.url import UrlService

#


# TODO: make configurable via settings/env?
_allow_header_real_ip       = True
_allow_header_forwarded_for = True
_client_ip_first            = False


primary_endpoint = APIRouter(prefix='', tags=['api', 'primary'])



async def _get_client_ip(req: Request) -> str:
    if (real_ip := req.headers.get('X-Real-IP')) and _allow_header_real_ip:
        return real_ip

    elif (forwarded_for := req.headers.get('X-Forwarded-For')) and _allow_header_forwarded_for:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For
        # https://habr.com/ru/companies/k2tech/articles/1045012/
        index = 0 if _client_ip_first else -1
        return forwarded_for.split(',')[index].strip()

    elif addr := req.client:
        return addr.host

    return '0.0.0.0'



async def _get_client_referer(req: Request) -> str | None:
    if referer := req.headers.get('Referer'):
        try:
            return urlsplit(referer, allow_fragments=False).hostname
        except ValueError:
            pass
    return None


FRONTEND_LOGIN_PAGE = '/login'


@primary_endpoint.get('/u/{url_id}')
async def visit_url(
    req: Request,
    url_id: Annotated[str, Path()],
    auth_service: Annotated[AuthService, Depends()],
    clicks_service: Annotated[ClicksService, Depends()],
    security_service: Annotated[SecurityService, Depends()],
    url_service: Annotated[UrlService, Depends()],
    session_id: Annotated[str | None, Depends(get_current_session_id)] = None,
) -> Response:
    # parameter validation
    url = await url_service.get_url_by_id(url_id)

    # access checks
    if not await security_service.is_url_active(url):
        raise UrlNotFoundError(url_id)

    if not await security_service.is_url_freely_accessible(url):
        session = await get_current_session(auth_service, session_id)
        user    = await get_current_user(auth_service, session)
        if not await security_service.can_url_be_visited_by(user, url):
            return RedirectResponse(
                url=f"{FRONTEND_LOGIN_PAGE}?{urlencode({ 'redirect': req.url.path })}",
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            )

    # client info retrieval
    visitor = UrlVisitorMetadata(
        ip                      = await _get_client_ip(req),
        headers_user_agent      = req.headers.get('User-Agent'),
        headers_accept_language = req.headers.get('Accept-Language'),
        headers_referer_domain  = await _get_client_referer(req),
    )

    # log every visit accurately (before allowing the client to proceed)
    await clicks_service.register_url_visit(url.id, visitor)

    # respond
    return RedirectResponse(
        url=url.original_url,
        status_code=status.HTTP_303_SEE_OTHER,
        headers={},
    )

