from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db_session

#


class BaseService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        assert db is not None
        self.db = db

