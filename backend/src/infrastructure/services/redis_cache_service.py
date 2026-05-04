import redis.asyncio as aioredis

from src.domain.services.cache_service import AbstractCacheService


class RedisCacheService(AbstractCacheService):
    def __init__(self, redis_url: str) -> None:
        self._redis: aioredis.Redis | None = None
        self._url = redis_url

    async def connect(self) -> None:
        self._redis = await aioredis.from_url(self._url, decode_responses=True)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()

    async def get(self, key: str) -> str | None:
        if not self._redis:
            return None
        try:
            return await self._redis.get(key)
        except Exception:
            return None

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        if not self._redis:
            return
        try:
            await self._redis.set(key, value, ex=ttl_seconds)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        if not self._redis:
            return
        try:
            await self._redis.delete(key)
        except Exception:
            pass

    async def invalidate_pattern(self, pattern: str) -> None:
        if not self._redis:
            return
        try:
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass
