import random
import re
import string
import uuid
from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError

from backend.db.database import now_UTC
from backend.models.url import Url
from backend.models.user import User
from backend.schemas.url import UrlCreate
from backend.services.base import BaseService
from backend.services.exceptions import UrlNotFoundError

#

URL_ID_MIN_LEN = 10
URL_ID_MAX_LEN = 10
if URL_ID_MIN_LEN == URL_ID_MAX_LEN:
    URL_ID_PATTERN = f"[a-zA-Z0-9]{{{URL_ID_MAX_LEN}}}"
else:
    URL_ID_PATTERN = f"[a-zA-Z0-9]{{{URL_ID_MIN_LEN}-{URL_ID_MAX_LEN}}}"
URL_ID_PATTERN_RE = re.compile(URL_ID_PATTERN)

_URL_ID_CHARACTERS = string.ascii_letters + string.digits


URL_SORTING_CRITERIA: dict[str, object] = {
    'id':      func.lower(Url.id),
    'created': Url.created_at,
    'updated': Url.updated_at,
    'expires': Url.expires_at,
    'title':   func.lower(Url.title),
    'url':     Url.original_url,
    # others make little to no sense (to me) or require using join(s)
}
URL_SORTING_CRITERIA_DEFAULT = Url.updated_at


class UrlCategory(StrEnum):
    OPEN     = auto()
    PRIVATE  = auto()
    ACTIVE   = auto()
    EXPIRED  = auto()
    DISABLED = auto()

    @classmethod
    def _missing_(cls, _: object) -> 'UrlCategory | None':
        return UrlCategory.OPEN


class UrlService(BaseService):

    async def create_new_url(self, owner: User, url_info: UrlCreate) -> Url:
        while True:
            try:
                url_id = ''.join(random.choices(_URL_ID_CHARACTERS, k=URL_ID_MAX_LEN))

                url = Url(
                    id=url_id,
                    owner_id=owner.id,
                    **url_info.model_dump(),
                )

                self.db.add(url)
                await self.db.commit()

                await self.db.refresh(url)
                return url  # TODO: cache?
            except IntegrityError:
                pass


    async def find_url_by_id(self, url_id: str) -> Url | None:
        return await self.db.get(Url, url_id)


    async def get_url_by_id(self, url_id: str) -> Url:
        if URL_ID_PATTERN_RE.fullmatch(url_id) is None or (url := await self.find_url_by_id(url_id)) is None:
            raise UrlNotFoundError(url_id)
        else:
            return url


    @staticmethod
    def _apply_category_filter(stmt: Select, category: UrlCategory | None, now_utc: datetime) -> Select:
        if category is None:
            return stmt
        match category:
            case UrlCategory.OPEN:
                return stmt.where(
                    Url.is_open_access
                )
            case UrlCategory.PRIVATE:
                return stmt.where(
                    ~Url.is_open_access
                )
            case UrlCategory.ACTIVE:
                return stmt.where(
                    Url.is_active & (Url.expires_at.is_(None) | (now_utc < Url.expires_at))
                )
            case UrlCategory.EXPIRED:
                return stmt.where(
                    Url.is_active & (Url.expires_at <= now_utc)
                )
            case UrlCategory.DISABLED:
                return stmt.where(
                    ~Url.is_active
                )


    async def find_urls_batched(
        self,
        *,
        offset_items: int = 0,
        batch_size: int = 50,
        owner: User | uuid.UUID | None = None,
        text: str = '',
        sort_criteria: str = 'updated',
        sort_asc: bool = False,
        url_category: UrlCategory | None = None,
        now_utc: datetime | None = None,
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
            stmt = stmt.where(Url.title.icontains(text) | Url.description.icontains(text) | (Url.id == text))

        # type label filtering
        if url_category is not None:
            stmt = self._apply_category_filter(stmt, url_category, now_utc or now_UTC())

        # ordering/sorting
        criteria = URL_SORTING_CRITERIA.get(sort_criteria.lower(), URL_SORTING_CRITERIA_DEFAULT)
        if not sort_asc:
            criteria = criteria.desc()  # type: ignore  # no idea what type to use for dict values
        stmt = stmt.order_by(criteria)  # type: ignore

        if criteria is not Url.id:
            stmt = stmt.order_by(Url.id)

        # shift and truncation
        stmt = stmt.offset(offset_items).limit(batch_size)

        # fetch
        rows = await self.db.execute(stmt)
        return rows.scalars().all()

