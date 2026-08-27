import logging
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import password_get_hash
from backend.db.database import get_db_session_context
from backend.models.user import User

#

logger = logging.getLogger()



async def upsert_primary_superuser() -> None:
    try:
        async with get_db_session_context() as session:
            await create_user(
                session,
                email='admin@url-shortener.internal',
                name='admin',
                pwd='admin',
                is_privileged=True,
            )
    except IntegrityError:
        logger.info('Primary superuser already present, skipping.')



def _normalize_email(email: str) -> str:
    return email.strip().lower()



async def create_user(
    db: AsyncSession,
    email: str, name: str, pwd: str,
    *,
    is_privileged: bool = False,
) -> User:
    user = User(
        email=_normalize_email(email),
        name=name,
        hashed_password=password_get_hash(pwd),
        is_active=True,
        is_superuser=is_privileged,
    )

    db.add(user)
    await db.commit()

    await db.refresh(user)
    return user



async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    assert user_id

    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    assert email

    res = await db.execute(
        select(User).where(User.email == _normalize_email(email))
    )
    return res.scalar_one_or_none()



async def get_all_users_batched(db: AsyncSession, *, offset_items: int = 0, batch_size: int = 50) -> Sequence[User]:
    assert batch_size >= 0
    assert offset_items >= 0

    res = await db.execute(
        select(User).order_by(User.name, User.id).offset(offset_items).limit(batch_size)
    )
    return res.scalars().all()


