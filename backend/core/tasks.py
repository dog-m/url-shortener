import asyncio
from collections.abc import Awaitable

#


def periodic_task(interval: float):
    def wrapper(func: Awaitable):
        async def impl(*args, **kw):
            while True:
                await func(*args, **kw)
                await asyncio.sleep(interval)
        return impl
    return wrapper
