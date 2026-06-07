from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db_session

#


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login')


auth_router = APIRouter(prefix='/api/v1')


@auth_router.post('/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    return {
        'user': form_data.username,
        'pwd': form_data.password,
        'db': f"{db!r}",
    }
