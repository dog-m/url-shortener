from typing import Annotated
from urllib.parse import urlencode, urlsplit

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import (
    get_current_session,
    get_current_session_id,
    get_current_user,
)
from backend.db.database import get_db_session
from backend.models.click import UrlVisitorMetadata
from backend.services.security import can_url_be_visited_by, is_url_freely_accessible
from backend.services.url import URL_ID_PATTERN, find_url_by_id, register_url_visit

#


# TODO: make configurable via settings/env?
_allow_header_real_ip       = True
_allow_header_forwarded_for = True
_client_ip_first            = False


api_urls_router = APIRouter(prefix='', tags=['api', 'urls'])



async def _get_client_ip(req: Request) -> str:
    if real_ip := req.headers.get('X-Real-IP') and _allow_header_real_ip:
        return real_ip

    elif forwarded_for := req.headers.get('X-Forwarded-For') and _allow_header_forwarded_for:
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


@api_urls_router.get('/u/{url_id}')
async def visit_url(
    req: Request,
    url_id: Annotated[str, Path()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session_id: Annotated[str | None, Depends(get_current_session_id)] = None,
):
    # parameter validation
    if URL_ID_PATTERN.fullmatch(url_id) is None or (url := await find_url_by_id(db, url_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # access checks
    if not await is_url_freely_accessible(url):
        session = await get_current_session(db, session_id)
        user    = await get_current_user(db, session)
        if not user or not await can_url_be_visited_by(user, url):
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
    await register_url_visit(db, url, visitor)

    # respond
    return RedirectResponse(
        url=url.original_url,
        status_code=status.HTTP_303_SEE_OTHER,
        headers={},
    )

