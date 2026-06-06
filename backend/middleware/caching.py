from asyncio import Lock
from datetime import datetime, timedelta


class AsyncFileContentCache:
    def __init__(self, base_dir: str = '.'):
        self._lock = Lock()
        self._files: dict[str, tuple[datetime, bytes]] = {}
        self._base_dir = base_dir
        self._delta = timedelta(seconds=30)


    async def get(self, filename: str) -> bytes:
        if (entry := self._files.get(filename)) is None:
            pass
            entry = (1, 1)

        last_access, data = entry
        if datetime.now() - last_access >= self._delta:
            async with self._lock:
                pass

        return data


