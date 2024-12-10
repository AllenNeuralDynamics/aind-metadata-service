"""Module for handling redis session"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from aind_metadata_service.backends.redis.configs import Settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Add session to lifespan of app"""
    settings = Settings()
    redis = aioredis.from_url(settings.connection_str)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
