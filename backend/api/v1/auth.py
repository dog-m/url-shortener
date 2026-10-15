from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from backend.api.dependencies import (
    SESSION_COOKIE_NAME,
    get_current_session,
    html_redirect,
)
from backend.core.config import settings
from backend.core.security import password_verify
from backend.models.session import Session
from backend.services.auth import AuthService
from backend.services.user import UserService

#


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login')  # TODO: ???


FRONTEND_INDEX     = '/'
FRONTEND_USER_MAIN = '/profile'


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login')
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends()],
    auth_service: Annotated[AuthService, Depends()],
    redirect: Annotated[str, Query()] = FRONTEND_USER_MAIN,
) -> Response:
    if not redirect.startswith('/'):  # only allow endpoints on this site
        redirect = FRONTEND_USER_MAIN

    user = await user_service.find_user_by_email(form_data.username)
    if not user or not user.hashed_password or not password_verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    session = await auth_service.new_session(user)

    res = html_redirect(redirect)
    res.set_cookie(
        SESSION_COOKIE_NAME, session.id,
        httponly=True,
        expires=settings.user_session_expire_days * 24 * 3600,
    )
    return res



@router.post('/logout')
async def logout(
    auth_service: Annotated[AuthService, Depends()],
    session: Annotated[Session | None, Depends(get_current_session)] = None,
) -> Response:
    if session is not None:
        await auth_service.terminate_session(session)

    res = html_redirect(FRONTEND_INDEX)
    res.delete_cookie(SESSION_COOKIE_NAME)
    return res

