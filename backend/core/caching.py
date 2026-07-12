from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.coder import PickleCoder
from redis.asyncio import Redis

from backend.core.config import settings

#


# https://github.com/long2ice/fastapi-cache/issues/562
class ClearedInMemoryBackend(InMemoryBackend):

    async def clear_expired(self) -> None:
        async with self._lock:
            # collect keys for removal
            now = self._now
            keys_to_remove = tuple(
                k
                for k, v in self._store.items()
                if now > v.ttl_ts
            )

            # do removal here separately
            for k in keys_to_remove:
                del self._store[k]



async def init_caches() -> None:
    if settings.redis_url is not None:
        backend = RedisBackend(Redis.from_url(settings.redis_url))
    else:
        backend = ClearedInMemoryBackend()

    FastAPICache.init(
        backend,
        expire=settings.cache_ttl,
        cache_status_header=settings.cache_status_header,
        coder=PickleCoder,
    )



async def clear_caches() -> None:
    await FastAPICache.get_backend().clear()
