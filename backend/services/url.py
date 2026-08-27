import random
import re
import string
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from backend.models.click import UrlVisitorMetadata
from backend.models.url import Url
from backend.models.user import User
from backend.schemas.url import UrlCreate, UrlUpdate

#

URL_ID_MIN_LEN = 10
URL_ID_MAX_LEN = 10
URL_ID_PATTERN = None
if URL_ID_MIN_LEN == URL_ID_MAX_LEN:
    URL_ID_PATTERN = re.compile(f"[a-zA-Z0-9]{{{URL_ID_MAX_LEN}}}")
else:
    URL_ID_PATTERN = re.compile(f"[a-zA-Z0-9]{{{URL_ID_MIN_LEN}-{URL_ID_MAX_LEN}}}")


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



async def find_url_by_id(db: AsyncSession, url_id: str, *, lock: bool = False) -> Url | None:
    stmt = select(Url).where(Url.id == url_id)

    if lock:
        stmt = stmt.with_for_update(key_share=True)

    return (await db.execute(stmt)).scalar()



_FIND_URLS__SORTING_CRITERIA: dict[str, InstrumentedAttribute] = {
    'id':      Url.id,
    'created': Url.created_at,
    'updated': Url.updated_at,
    'expires': Url.expires_at,
    'title':   Url.title,
    'url':     Url.original_url,
    # others make little to no sense (to me) or require using join
}

_FIND_URLS__DEFAULT_SORTING = Url.updated_at


async def find_urls_batched(
    db: AsyncSession,
    *,
    offset_items: int = 0,
    batch_size: int = 50,
    owner: User | UUID | None = None,
    text: str = '',
    sort_criteria: str = 'updated',
    sort_asc: bool = False,
) -> Sequence[Url]:
    stmt = select(Url)

    # filtering
    if owner is not None:
        if isinstance(owner, User):
            stmt = stmt.where(Url.owner_id == owner.id)
        else:
            stmt = stmt.where(Url.owner_id == owner)
    text = text.strip()
    if text:
        text = text.replace('%', '\\%')
        text = '%'.join(text.split())
        stmt = stmt.where(Url.title.icontains(text) | Url.description.icontains(text))

    # ordering/sorting
    criteria = _FIND_URLS__SORTING_CRITERIA.get(sort_criteria.lower(), _FIND_URLS__DEFAULT_SORTING)
    if not sort_asc:
        criteria = criteria.desc()
    stmt = stmt.order_by(criteria)

    if criteria is not Url.id:
        stmt = stmt.order_by(Url.id)

    # shift and truncation
    stmt = stmt.offset(offset_items).limit(batch_size)

    # fetch
    rows = await db.execute(stmt)
    return rows.scalars().all()



async def update_url(db: AsyncSession, url_patch: UrlUpdate) -> None:
    await db.execute(
        update(Url), [url_patch.model_dump()]
    )
    await db.commit()


async def register_url_visit(db: AsyncSession, url: Url, visitor: UrlVisitorMetadata) -> None:
    # TODO: log user clicks
    print(f"[~] Url /u/{url.id} has been visited by {visitor!r}")
    pass

