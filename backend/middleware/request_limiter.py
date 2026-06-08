import time
from dataclasses import dataclass

from fastapi import Response
from fastapi.middleware import Middleware
from fastapi.responses import HTMLResponse
from starlette.types import ASGIApp, Receive, Scope, Send

#


@dataclass(slots=True, frozen=True, eq=False)
class RequestCacheEntry:
    id: str
    requests_budget: int
    next_refresh: float



class RequestLimiterCache:
    def __init__(self):
        self.records: dict[str, RequestCacheEntry] = {}

    async def get_entry(self, key: str) -> RequestCacheEntry | None:
        return self.records.get(key)

    async def set_entry(self, entry: RequestCacheEntry) -> None:
        self.records[entry.id] = entry



# https://fastapi.tiangolo.com/advanced/middleware/
class RequestLimiter(Middleware):
    def __init__(
        self,
        app: ASGIApp,
        cache: RequestLimiterCache,
        entry_budget: int = 10,  # count
        refresh_window: float = 5.0,  # seconds
        abuse_penalty_multiplier: float = 2.0,  # seconds
        abuse_budget_cutoff: int = -10,  # count
    ) -> None:
        assert entry_budget > 0
        assert refresh_window > 0.0
        assert abuse_penalty_multiplier > 0.0
        assert abuse_budget_cutoff <= 0
        self.app = app
        self.cache = cache
        self.entry_budget = entry_budget
        self.refresh_window = refresh_window
        self.abuse_penalty_multiplier = abuse_penalty_multiplier
        self.abuse_budget_cutoff = abuse_budget_cutoff


    async def is_too_many(self, scope: Scope) -> bool:
        if addr := scope.get("client"):  # ip+port
            client_id = str(addr[0])
            current_time = time.time()

            if entry := await self.cache.get_entry(client_id):
                # the client has sent requests to us already

                # update stats
                new_budget  = entry.requests_budget - 1
                new_refresh = entry.next_refresh

                # avoid hammering cache too much with misbehaving clients
                if new_budget < self.abuse_budget_cutoff:
                    return True

                if new_budget < 0:
                    if current_time < new_refresh:
                        # too early to have a refresh - apply discouraging measures
                        new_refresh += self.abuse_penalty_multiplier
                    else:
                        # refresh entry
                        new_budget  = self.entry_budget
                        new_refresh = current_time + self.refresh_window

                # sync
                await self.cache.set_entry(RequestCacheEntry(
                    id=client_id,
                    requests_budget=new_budget,
                    next_refresh=new_refresh,
                ))

                return new_budget < 0

            else:
                # first time meeting this client
                await self.cache.set_entry(RequestCacheEntry(
                    id=client_id,
                    requests_budget=self.entry_budget,
                    next_refresh=current_time + self.refresh_window,
                ))

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


