from datetime import datetime, timedelta

from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


class CacheManager:
    def __init__(
        self,
        redis_dsn: str,
        prefix: str,
        reset_hour: int,
        reset_minute: int,
    ) -> None:
        self._redis_dsn = redis_dsn
        self._prefix = prefix
        self._reset_hour = reset_hour
        self._reset_minute = reset_minute
        self._redis_client: aioredis.Redis | None = None
        self._backend: RedisBackend | None = None

    def get_namespace(self, namespace: str = "") -> str:
        return f"{self._prefix}:{namespace}" if namespace else self._prefix

    def get_backend(self) -> RedisBackend:
        if self._backend is None:
            self._redis_client = aioredis.from_url(
                self._redis_dsn,
                encoding="utf-8",
                decode_responses=False,
            )
            self._backend = RedisBackend(self._redis_client)
        return self._backend

    def seconds_until_reset(self, now: datetime | None = None) -> int:
        current_time = now or datetime.now()
        reset_at = current_time.replace(
            hour=self._reset_hour,
            minute=self._reset_minute,
            second=0,
            microsecond=0,
        )
        if current_time >= reset_at:
            reset_at += timedelta(days=1)
        return max(1, int((reset_at - current_time).total_seconds()))

    async def close(self) -> None:
        if self._redis_client is not None:
            await self._redis_client.close()
        self._redis_client = None
        self._backend = None
