import random
import string
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.url import URL_ID_MAX_LEN, Url
from backend.models.user import User
from backend.schemas.url import UrlCreate

#


_URL_ID_CHARACTERS = string.ascii_letters + string.digits


async def create_new_url(db: AsyncSession, owner: User, url_info: UrlCreate) -> Url:
    while True:
        try:
            url_id = ''.join(random.choices(_URL_ID_CHARACTERS, k=URL_ID_MAX_LEN))

            url = Url(
                id=url_id,
                original_url=url_info.original_url.encoded_string(),
                is_active=False,
                title=url_info.title,
                description=url_info.description,
                owner_id=owner.id,
            )

            db.add(url)
            await db.commit()

            await db.refresh(url)
            # TODO: cache?
            return url
        except IntegrityError:
            pass



async def list_user_urls(db: AsyncSession, user: User, *, offset: int = 0, page_size: int = 50) -> Sequence[Url]:
    rows = await db.execute(
        select(Url).where(Url.owner_id == user.id).order_by(Url.updated_at.desc()).offset(offset).limit(page_size)
    )
    return rows.scalars().all()

