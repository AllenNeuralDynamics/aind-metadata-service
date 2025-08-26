"""Module to handle sessions to different backends."""

from typing import AsyncGenerator

import aind_labtracks_service_async_client
import aind_mgi_service_async_client
from httpx import AsyncClient

from aind_metadata_service_server.configs import get_settings

settings = get_settings()
labtracks_config = aind_labtracks_service_async_client.Configuration(
    host=settings.labtracks_host.unicode_string().strip("/")
)
mgi_config = aind_mgi_service_async_client.Configuration(
    host=settings.mgi_host.unicode_string().strip("/")
)


async def get_labtracks_api_instance() -> (
    AsyncGenerator[aind_labtracks_service_async_client.DefaultApi, None]
):
    """
    Yield an aind_labtracks_service_async_client.DefaultApi object.
    """
    async with aind_labtracks_service_async_client.ApiClient(
        labtracks_config
    ) as api_client:
        api_instance = aind_labtracks_service_async_client.DefaultApi(
            api_client
        )
        yield api_instance


async def get_mgi_api_instance() -> (
    AsyncGenerator[aind_mgi_service_async_client.DefaultApi, None]
):
    """
    Yield an aind_mgi_service_async_client.DefaultApi object.
    """
    async with aind_mgi_service_async_client.ApiClient(
        mgi_config
    ) as api_client:
        api_instance = aind_mgi_service_async_client.DefaultApi(api_client)
        yield api_instance


async def get_aind_data_schema_v1_session() -> (
    AsyncGenerator[AsyncClient, None]
):
    """
    Yield an async session object. This will automatically close the session
    when finished.
    """
    async with AsyncClient(
        base_url=settings.aind_data_schema_v1_host.unicode_string()
    ) as session:
        yield session
