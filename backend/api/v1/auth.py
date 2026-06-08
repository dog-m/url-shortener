from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import new_html_redirector
from backend.db.database import get_db_session

#


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login')

AUTH_COOKIE_NAME = 'u-auth'

FRONTEND_INDEX     = '/'
FRONTEND_USER_MAIN = '/user'


api_auth_router = APIRouter(prefix='/api/v1', tags=['api', 'auth'])


@api_auth_router.post('/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    res = new_html_redirector(FRONTEND_USER_MAIN)
    res.set_cookie(AUTH_COOKIE_NAME, '123', httponly=True)
    return res



@api_auth_router.get('/logout')
async def logout(
    req: Request,
    session: AsyncSession = Depends(get_db_session),
):
    res = new_html_redirector(FRONTEND_INDEX)
    res.delete_cookie(AUTH_COOKIE_NAME)
    return res

