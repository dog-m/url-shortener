from html import escape
from typing import Annotated

from fastapi import Cookie, Depends, Response
from fastapi.responses import HTMLResponse

from backend.models.session import SESSION_ID_MAX_LEN, Session
from backend.models.user import User
from backend.services.auth import AuthService
from backend.services.exceptions import AccessDeniedError

#


def html_redirect(target_url: str, *, delay_sec: int = 1) -> Response:
    assert delay_sec >= 0

    return HTMLResponse(
        content=f"""<!DOCTYPE html>
        <html>
            <head>
                <title>...</title>
                <meta http-equiv="refresh" content="{delay_sec};url={escape(target_url)}" />
                <style>
                    body {{ background: #fff; }}
                    @media (prefers-color-scheme:dark) {{
                        body {{ background: #000; }}
                    }}
                </style>
            </head>
            <body></body>
        </html>""",
    )



SESSION_COOKIE_NAME = 'u_session'


async def get_current_session_id(
    u_session: Annotated[str | None, Cookie(max_length=SESSION_ID_MAX_LEN)] = None,
) -> str | None:
    return u_session


async def get_current_session(
    auth_service: Annotated[AuthService, Depends()],
    session_id: Annotated[str | None, Depends(get_current_session_id)] = None,
) -> Session | None:
    if session_id is None:
        return None

    return await auth_service.get_active_session_by_id(session_id)



async def get_current_user(
    auth_service: Annotated[AuthService, Depends()],
    session: Annotated[Session | None, Depends(get_current_session)] = None,
) -> User | None:
    if session and (user := await auth_service.get_user_by_session(session)) and user.is_active:
        return user
    else:
        return None



async def require_user(
    user: Annotated[User | None, Depends(get_current_user)] = None,
) -> User:
    if user:
        return user
    else:
        raise AccessDeniedError()



async def require_admin(
    user: Annotated[User, Depends(require_user)],
) -> User:
    if user.is_superuser:
        return user
    else:
        raise AccessDeniedError()
