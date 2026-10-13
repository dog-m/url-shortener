import logging
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.core.config import settings
from backend.core.security import password_get_hash
from backend.models.user import User
from backend.services.base import BaseService

#

logger = logging.getLogger()


class UserService(BaseService):

    async def upsert_default_users(self) -> None:
        try:
            await self.create_user(
                email='admin@url-shortener.internal',
                name='admin',
                pwd='admin',
                is_privileged=True,
            )
        except IntegrityError:
            logger.info('Primary superuser already present, skipping.')

        # adding regular user
        if settings.playwright_test:
            await self.create_user(
                email='user@url-shortener.internal',
                name='user',
                pwd='user',
                is_privileged=False,
            )


    async def _normalize_email(self, email: str) -> str:
        return email.strip().lower()


    async def create_user(
            self,
            email: str, name: str, pwd: str,
            *,
            is_privileged: bool = False,
        ) -> User:
        user = User(
            email=await self._normalize_email(email),
            name=name,
            hashed_password=password_get_hash(pwd),
            is_active=True,
            is_superuser=is_privileged,
        )

        self.db.add(user)
        await self.db.commit()

        await self.db.refresh(user)
        return user


    async def get_user_by_id(self, user_id: UUID) -> User | None:
        assert user_id is not None

        return await self.db.get(User, user_id)


    async def get_user_by_email(self, email: str) -> User | None:
        assert email

        res = await self.db.execute(
            select(User).where(User.email == await self._normalize_email(email))
        )
        return res.scalar_one_or_none()


    async def find_users_batched(self, *, offset_items: int = 0, batch_size: int = 50) -> Sequence[User]:
        assert batch_size >= 0
        assert offset_items >= 0

        stmt = select(User)

        stmt = stmt.order_by(User.name, User.id).offset(offset_items).limit(batch_size)

        res = await self.db.execute(stmt)
        return res.scalars().all()

