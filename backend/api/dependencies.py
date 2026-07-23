from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.db.database import get_db_session
from backend.models.session import Session
from backend.models.user import User
from backend.services.auth import get_active_session_by_id, get_user_by_session

#


def new_html_redirector(target_url: str, *, delay_sec: int = 1) -> Response:
    assert delay_sec >= 0

    return HTMLResponse(
        content=f'''<!DOCTYPE html>
        <html>
            <head>
                <title>...</title>
                <meta http-equiv="refresh" content="{delay_sec};url={target_url}" />
            </head>
            <body></body>
        </html>''',
    )



SESSION_COOKIE_NAME = 'u_session'


async def get_current_session(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    u_session: Annotated[str | None, Cookie()] = None,
) -> Session | None:
    if u_session is None:
        return None

    return await get_active_session_by_id(db, u_session)



async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session: Annotated[Session | None, Depends(get_current_session)] = None,
) -> User | None:
    if session is None:
        return None

    return await get_user_by_session(db, session)



async def require_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User | None, Depends(get_current_user)] = None,
) -> User:
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
