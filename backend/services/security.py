from backend.db.database import now_UTC
from backend.models.url import Url
from backend.models.user import User
from backend.services.base import BaseService
from backend.services.exceptions import InsufficientPrivilegesError, UrlNotFoundError

#


class SecurityService(BaseService):

    async def is_url_active(self, url: Url) -> bool:
        if not url.is_active:
            return False

        if url.expires_at:
            if url.expires_at <= now_UTC().replace(tzinfo=None):
                return False

        return True


    async def is_url_freely_accessible(self, url: Url) -> bool:
        # TODO: more complex rules?
        return url.is_open_access


    async def is_visible_for(self, user: User | None, url: Url) -> bool:
        # TODO: unnecessary? other rules?
        return url.is_open_access or user is not None


    async def _check_manage(self, user: User, url: Url) -> bool:
        return url.owner_id == user.id or user.is_superuser


    async def can_manage_url(self, user: User, url: Url) -> None:
        if not await self._check_manage(user, url):
            raise InsufficientPrivilegesError()


    async def can_manage_url_or_missing(self, user: User, url: Url) -> None:
        if not await self._check_manage(user, url):
            raise UrlNotFoundError(url.id)
