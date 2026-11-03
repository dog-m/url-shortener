import math
import secrets
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from backend.core.config import settings
from backend.core.tasks import periodic_task
from backend.db.database import get_db_session_context, now_UTC
from backend.models.session import SESSION_ID_MAX_LEN, Session
from backend.models.user import User
from backend.services.base import BaseService

#


class AuthService(BaseService):

    async def _generate_session_id(self) -> str:
        nbytes = math.ceil(SESSION_ID_MAX_LEN * 3 / 4)
        return secrets.token_urlsafe(nbytes)[:SESSION_ID_MAX_LEN]


    async def new_session(self, user: User) -> Session:
        while True:
            try:
                session = Session(
                    id=await self._generate_session_id(),
                    user_id=user.id,
                    expires_at=datetime.now(UTC) + timedelta(days=settings.user_session_expire_days),
                )

                self.db.add(session)
                await self.db.commit()
                await self.db.refresh(session)

                pass # TODO: cache session info?

                return session

            except IntegrityError:
                await self.db.rollback()  # clear transaction to continue using the same session


    async def get_active_session_by_id(self, session_id: str) -> Session | None:
        rows = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        if session := rows.scalar():
            if datetime.now(UTC).replace(tzinfo=None) < session.expires_at:
                return session

        return None


    async def get_user_by_session(self, session: Session) -> User | None:
        rows = await self.db.execute(
            select(User).where(User.id == session.user_id)
        )
        return rows.scalar_one_or_none()


    async def get_user_sessions(self, user: User) -> Sequence[Session]:
        rows = await self.db.execute(
            select(Session).where(Session.user_id == user.id)
        )
        return rows.scalars().all()


    async def terminate_session(self, session: Session) -> None:
        await self.db.execute(
            delete(Session).where(Session.id == session.id)
        )
        await self.db.commit()
        # TODO: update cache?


    async def terminate_all_sessions(self, user: User) -> None:
        await self.db.execute(
            delete(Session).where(Session.user_id == user.id)
        )
        await self.db.commit()


    async def terminate_expired(self) -> None:
        await self.db.execute(
            delete(Session).where(now_UTC() > Session.expires_at)
        )
        await self.db.commit()



@periodic_task(60)
async def task_remove_stale_sessions() -> None:
    async with get_db_session_context() as db:
        await AuthService(db).terminate_expired()

