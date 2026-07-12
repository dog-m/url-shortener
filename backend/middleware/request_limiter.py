import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from fastapi import Response, status
from fastapi.middleware import Middleware
from fastapi.responses import HTMLResponse
from fastapi_cache import FastAPICache
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

#


@dataclass(slots=True, frozen=True, eq=False)
class RequestCacheEntry:
    request_budget: int
    next_refresh: float



class RequestLimiterCache(ABC):

    @abstractmethod
    async def get_entry(self, key: str) -> RequestCacheEntry | None: ...

    @abstractmethod
    async def set_entry(self, id: str, request_budget: int, next_refresh: float) -> None: ...



# NOTE: there is no management of stale entries that are accessed very rarely
class DefaultRateLimiterCache(RequestLimiterCache):
    def __init__(self, entry_prefix: str = 'rate-limiter'):
        self.entry_prefix = entry_prefix


    def _with_prefix(self, key: str) -> str:
        return f"{self.entry_prefix}+{key}"


    @override
    async def get_entry(self, key: str) -> RequestCacheEntry | None:
        k = self._with_prefix(key)
        if data := await FastAPICache.get_backend().get(k):
            try:
                obj = FastAPICache.get_coder().decode(data)
                if isinstance(obj, RequestCacheEntry):
                    return obj
                elif isinstance(obj, dict):
                    return RequestCacheEntry(**obj)
            except Exception:
                # reset this entry on the subsequent call to 'set_*'
                pass
        return None


    @override
    async def set_entry(self, id: str, request_budget: int, next_refresh: float) -> None:
        entry = RequestCacheEntry(
            request_budget=request_budget,
            next_refresh=next_refresh,
        )
        await FastAPICache.get_backend().set(
            key=self._with_prefix(id),
            value=FastAPICache.get_coder().encode(entry),
            expire=int(entry.next_refresh + 1),  # probably requires manual cleanup for stale/infrequent entries
        )



RATE_LIMITER_DEFAULT_RESPONSE = '''
<!DOCTYPE html>
<html>
    <head><title>429 - Too Many Requests</title></head>
    <body><h1>Too Many Requests</h1></body>
</html>
'''



# https://fastapi.tiangolo.com/advanced/middleware/
class RequestLimiter(Middleware):
    def __init__(
        self,
        app: ASGIApp,
        cache: RequestLimiterCache,
        request_budget: int = 10,  # count
        refresh_window: float = 5.0,  # seconds
        abuse_penalty_multiplier: float = 2.0,  # seconds
        abuse_budget_cutoff: int = -10,  # count
        response_content: str | None = RATE_LIMITER_DEFAULT_RESPONSE,
        use_port_as_id: bool = False,  # NOTE: this might/will cause issues with clients behind NAT
        header_client_ip: str | None = None,  # might be 'X-Forwarded-For' or 'X-Real-IP'
        header_client_ip_first: bool = True,
    ) -> None:
        assert cache is not None
        assert request_budget > 0
        assert refresh_window > 0.0
        assert abuse_penalty_multiplier > 0.0
        assert abuse_budget_cutoff <= 0
        #
        self.app = app
        self.cache = cache
        self.request_budget = request_budget
        self.refresh_window = refresh_window
        self.abuse_penalty_multiplier = abuse_penalty_multiplier
        self.abuse_budget_cutoff = abuse_budget_cutoff
        self.response_content = response_content
        self.use_port_as_id = use_port_as_id
        self.header_client_ip = header_client_ip
        self.header_client_ip_first = header_client_ip_first


    async def _get_client_id(self, scope: Scope) -> str:
        # check special headers for client address when behind a proxy
        if header := self.header_client_ip:
            if value := Headers(scope=scope).get(header):
                index = 0 if self.header_client_ip_first else -1
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For
                # https://habr.com/ru/companies/k2tech/articles/1045012/
                return value.split(',')[index].strip()

        # fallback to using connection metadata if present
        if addr := scope.get('client'):  # ip+port
            return str(addr if self.use_port_as_id else addr[0])
        else:
            return '(0.0.0.0, 65535)'


    async def is_too_many(self, scope: Scope) -> bool:
        client_id = await self._get_client_id(scope)
        current_time = asyncio.get_running_loop().time()

        if entry := await self.cache.get_entry(client_id):
            # the client has sent requests to us already

            # update stats
            new_budget  = entry.request_budget - 1
            new_refresh = entry.next_refresh

            # avoid hammering cache too much with misbehaving clients
            if new_budget < self.abuse_budget_cutoff:
                if current_time < new_refresh:
                    # block until timeout
                    return True

            if new_budget <= 0:
                if current_time < new_refresh:
                    # too early to have a refresh - apply discouraging measures
                    new_refresh += self.abuse_penalty_multiplier
                else:
                    # refresh entry
                    new_budget  = self.request_budget
                    new_refresh = current_time + self.refresh_window

            # sync
            await self.cache.set_entry(
                id=client_id,
                request_budget=new_budget,
                next_refresh=new_refresh,
            )

            return new_budget <= 0

        else:
            # first time meeting this client
            await self.cache.set_entry(
                id=client_id,
                request_budget=self.request_budget,
                next_refresh=current_time + self.refresh_window,
            )

        return False


    async def build_response(self) -> Response:
        return HTMLResponse(
            content=self.response_content,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'lifespan' and await self.is_too_many(scope):
            response = await self.build_response()
            await response(scope, receive, send)

        else:
            await self.app(scope, receive, send)


