import math
import secrets
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.core.config import settings
from backend.models.session import SESSION_ID_MAX_LEN, Session
from backend.models.user import User

#


async def new_session(db: AsyncSession, user: User) -> Session:
    while True:
        try:
            nbytes = math.ceil(SESSION_ID_MAX_LEN * 3 / 4)
            session_id = secrets.token_urlsafe(nbytes)[:SESSION_ID_MAX_LEN]

            session = Session(
                id=session_id,
                user_id=user.id,
                expires_at=datetime.now(UTC) + timedelta(days=settings.user_session_expire_days),
            )

            db.add(session)
            await db.commit()

            await db.refresh(session)
            # TODO: cache
            return session
        except IntegrityError:
            pass



async def get_active_session_by_id(db: AsyncSession, session_id: str) -> Session | None:
    rows = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    if session := rows.scalar():
        if datetime.now(UTC).replace(tzinfo=None) < session.expires_at:
            return session

    return None



async def get_user_by_session(db: AsyncSession, session: Session) -> User | None:
    rows = await db.execute(
        select(User).where(User.id == session.user_id)
    )
    return rows.scalar_one_or_none()



async def get_user_sessions(db: AsyncSession, user: User) -> Sequence[Session]:
    rows = await db.execute(
        select(Session).where(Session.user_id == user.id)
    )
    return rows.scalars().all()



async def terminate_session(db: AsyncSession, session: Session) -> None:
    await db.execute(
        delete(Session).where(Session.id == session.id)
    )
    await db.commit()
    # TODO: update cache



async def terminate_all_sessions(db: AsyncSession, user: User) -> None:
    await db.execute(
        delete(Session).where(Session.user_id == user.id)
    )
    await db.commit()

