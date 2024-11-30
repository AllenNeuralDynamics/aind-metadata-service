from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi_cache.decorator import cache
from fastapi import FastAPI
from aind_metadata_service.backends.redis.configs import Settings as RedisSettings
from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = RedisSettings()
    redis = aioredis.from_url(settings.connection_str)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


# @cache()
# async def get_cache():
#     return 1
