import logging
from collections.abc import Sequence
from uuid import UUID

from pwdlib.hashers import HasherProtocol
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db_session
from backend.models.user import User

#

logger = logging.getLogger()


pwd_hasher: HasherProtocol = BcryptHasher()
pwd_salt = ''#settings.password_salt.encode()


def password_get_hash(password: str, salt: str | None = None) -> str:
    return pwd_hasher.hash(password, salt=salt)


def password_verify(plain_password: str, hashed_password: str) -> bool:
    return pwd_hasher.verify(plain_password, hashed_password)



async def upsert_primary_superuser() -> None:
    try:
        async for session in get_db_session():
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


