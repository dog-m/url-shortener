import time
from dataclasses import dataclass

from fastapi import Response
from fastapi.middleware import Middleware
from fastapi.responses import HTMLResponse
from fastapi_cache import FastAPICache
from starlette.types import ASGIApp, Receive, Scope, Send

#


@dataclass(slots=True, frozen=True, eq=False)
class RequestCacheEntry:
    request_budget: int
    next_refresh: float



# https://fastapi.tiangolo.com/advanced/middleware/
class RequestLimiter(Middleware):
    def __init__(
        self,
        app: ASGIApp,
        cache_prefix: str = 'rate-limiter',
        request_budget: int = 10,  # count
        refresh_window: float = 5.0,  # seconds
        abuse_penalty_multiplier: float = 2.0,  # seconds
        abuse_budget_cutoff: int = -10,  # count
    ) -> None:
        assert request_budget > 0
        assert refresh_window > 0.0
        assert abuse_penalty_multiplier > 0.0
        assert abuse_budget_cutoff <= 0
        self.app = app
        self.cache_prefix = cache_prefix
        self.request_budget = request_budget - 1
        self.refresh_window = refresh_window
        self.abuse_penalty_multiplier = abuse_penalty_multiplier
        self.abuse_budget_cutoff = abuse_budget_cutoff


    def get_prefixed_key(self, key: str) -> str:
        return f"{self.cache_prefix}+{key}"


    async def get_entry(self, key: str) -> RequestCacheEntry | None:
        k = self.get_prefixed_key(key)
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


    async def set_entry(self, id: str, request_budget: int, next_refresh: float) -> None:
        entry = RequestCacheEntry(
            request_budget=request_budget,
            next_refresh=next_refresh,
        )
        await FastAPICache.get_backend().set(
            key=self.get_prefixed_key(id),
            value=FastAPICache.get_coder().encode(entry),
            expire=int(entry.next_refresh + 1)
        )


    async def is_too_many(self, scope: Scope) -> bool:
        if addr := scope.get('client'):  # ip+port
            client_id = str(addr[0])
            current_time = time.time()

            if entry := await self.get_entry(client_id):
                # the client has sent requests to us already

                # update stats
                new_budget  = entry.request_budget - 1
                new_refresh = entry.next_refresh

                # avoid hammering cache too much with misbehaving clients
                if new_budget < self.abuse_budget_cutoff:
                    if current_time < new_refresh:
                        # block until timeout
                        return True

                if new_budget < 0:
                    if current_time < new_refresh:
                        # too early to have a refresh - apply discouraging measures
                        new_refresh += self.abuse_penalty_multiplier
                    else:
                        # refresh entry
                        new_budget  = self.request_budget
                        new_refresh = current_time + self.refresh_window

                # sync
                await self.set_entry(
                    id=client_id,
                    request_budget=new_budget,
                    next_refresh=new_refresh,
                )

                return new_budget < 0

            else:
                # first time meeting this client
                await self.set_entry(
                    id=client_id,
                    request_budget=self.request_budget,
                    next_refresh=current_time + self.refresh_window,
                )

        return False


    async def build_response(self) -> Response:
        return HTMLResponse(
            content='''<!DOCTYPE html>
            <html>
                <head><title>429 - Too Many Requests</title></head>
                <body><h1>Too Many Requests</h1></body>
            </html>''',
            status_code=429,
        )


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if await self.is_too_many(scope):
            response = await self.build_response()
            await response(scope, receive, send)

        else:
            await self.app(scope, receive, send)


