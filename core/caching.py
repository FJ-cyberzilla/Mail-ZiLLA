# core/caching.py
import asyncio
import pickle
from functools import wraps
from typing import Any, Optional

import redis


class RedisCache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=False)

    async def get(self, key: str) -> Optional[Any]:
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, self.redis.get, key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Cache get failed for key {key}: {str(e)}")
        return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        loop = asyncio.get_event_loop()
        try:
            serialized = pickle.dumps(value)
            return await loop.run_in_executor(
                None, self.redis.setex, key, expire, serialized
            )
        except Exception as e:
            self.logger.error(f"Cache set failed for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.redis.delete, key)


def cache_result(expire: int = 3600, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache()

            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire)

            return result

        return wrapper

    return decorator


from typing import Any, Optional


class RedisCache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=False)

    async def get(self, key: str) -> Optional[Any]:
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, self.redis.get, key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Cache get failed for key {key}: {str(e)}")
        return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        loop = asyncio.get_event_loop()
        try:
            serialized = pickle.dumps(value)
            return await loop.run_in_executor(
                None, self.redis.setex, key, expire, serialized
            )
        except Exception as e:
            self.logger.error(f"Cache set failed for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.redis.delete, key)


def cache_result(expire: int = 3600, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache()

            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire)

            return result

        return wrapper

    return decorator
