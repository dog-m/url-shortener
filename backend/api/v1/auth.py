from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import (
    SESSION_COOKIE_NAME,
    get_current_session,
    new_html_redirector,
)
from backend.core.config import settings
from backend.db.database import get_db_session
from backend.models.session import Session
from backend.services.auth import new_session, terminate_session
from backend.services.user import get_user_by_email, password_verify

#


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login')  # TODO: ???


FRONTEND_INDEX     = '/'
FRONTEND_USER_MAIN = '/user'


api_auth_router = APIRouter(prefix='', tags=['api', 'auth'])


@api_auth_router.post('/login')
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redirect: Annotated[str, Query()] = FRONTEND_USER_MAIN,
    id: Annotated[str | None, Cookie()] = None,
):
    print('[!!!]', id)  # TODO: log-in idempotency

    if not redirect.startswith('/'):  # only allow endpoints on this site
        redirect = FRONTEND_USER_MAIN

    user = await get_user_by_email(db, form_data.username)
    if not user or not password_verify(form_data.password, user.hashed_password):  # FIXME: user registration!
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    session = await new_session(db, user)

    res = new_html_redirector(redirect)
    res.set_cookie(SESSION_COOKIE_NAME, session.id, httponly=True, expires=settings.user_session_expire_days * 24 * 3600)
    return res



@api_auth_router.post('/logout')
async def logout(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session: Annotated[Session | None, Depends(get_current_session)] = None,
):
    if session is not None:
        await terminate_session(db, session)

    res = new_html_redirector(FRONTEND_INDEX)
    res.delete_cookie(SESSION_COOKIE_NAME)
    res.set_cookie('id', '987654321', httponly=True)  # TODO: log-in idempotency
    return res

