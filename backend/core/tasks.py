import asyncio
import functools
import inspect
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor

from backend.core.config import settings

#

_executor = ThreadPoolExecutor(
    max_workers=settings.periodic_tasks_pool_size,
    thread_name_prefix='periodic-task-worker-#',
)


def periodic_task(interval_sec: float):
    if interval_sec <= 0.0:
        raise AssertionError('Task run interval should be a positive value')

    def wrapper(func: Awaitable | Callable):
        # allow for non-async tasks/functions
        async def func_async(*args):
            await asyncio.get_running_loop().run_in_executor(_executor, func, *args)

        func_impl = func if inspect.iscoroutinefunction(func) else func_async

        @functools.wraps(func)
        async def wrapped(*args):
            while True:
                await asyncio.sleep(interval_sec)  # don't run all tasks on the app startup at the same time
                await func_impl(*args)

        return wrapped
    return wrapper

