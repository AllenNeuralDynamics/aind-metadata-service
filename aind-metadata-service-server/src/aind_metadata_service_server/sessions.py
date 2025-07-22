"""Module to handle sessions to different backends."""

from typing import AsyncGenerator

import aind_labtracks_service_async_client
import aind_mgi_service_async_client
import aind_sharepoint_service_async_client
import aind_session_json_service_async_client
import aind_slims_service_async_client
import aind_smartsheet_service_async_client
import aind_tars_service_async_client

from aind_metadata_service_server.configs import get_settings

settings = get_settings()
labtracks_config = aind_labtracks_service_async_client.Configuration(
    host=settings.labtracks_host.unicode_string().strip("/")
)
mgi_config = aind_mgi_service_async_client.Configuration(
    host=settings.mgi_host.unicode_string().strip("/")
)
smartsheet_config = aind_smartsheet_service_async_client.Configuration(
    host=settings.smartsheet_host.unicode_string().strip("/")
)
slims_config = aind_slims_service_async_client.Configuration(
    host=settings.slims_host.unicode_string().strip("/")
)
sharepoint_config = aind_sharepoint_service_async_client.Configuration(
    host=settings.sharepoint_host.unicode_string().strip("/")
)
tars_config = aind_tars_service_async_client.Configuration(
    host=settings.tars_host.unicode_string().strip("/")
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


async def get_smartsheet_api_instance() -> (
    AsyncGenerator[aind_smartsheet_service_async_client.DefaultApi, None]
):
    """
    Yield an aind_smartsheet_service_async_client.DefaultApi object.
    """
    async with aind_smartsheet_service_async_client.ApiClient(
        smartsheet_config
    ) as api_client:
        api_instance = aind_smartsheet_service_async_client.DefaultApi(
            api_client
        )
        yield api_instance


async def get_slims_api_instance() -> (
    AsyncGenerator[aind_slims_service_async_client.DefaultApi, None]
):
    """
    Yield an aind_slims_service_async_client.DefaultApi object.
    """
    async with aind_slims_service_async_client.ApiClient(
        slims_config
    ) as api_client:
        api_instance = aind_slims_service_async_client.DefaultApi(api_client)
        yield api_instance


async def get_sharepoint_api_instance() -> (
    AsyncGenerator[aind_sharepoint_service_async_client.DefaultApi, None]
):
    """
    Yield an aind_sharepoint_service_async_client.DefaultApi object.
    """
    async with aind_sharepoint_service_async_client.ApiClient(
        sharepoint_config
    ) as api_client:
        api_instance = aind_sharepoint_service_async_client.DefaultApi(
            api_client
        )
        yield api_instance


async def get_tars_api_instance() -> (
    AsyncGenerator[aind_tars_service_async_client.DefaultApi, None]
):
    """
    Yield an aind_tars_service_async_client.DefaultApi object.
    """
    async with aind_tars_service_async_client.ApiClient(
        tars_config
    ) as api_client:
        api_instance = aind_tars_service_async_client.DefaultApi(api_client)
        yield api_instance


async def get_session_json_api_instance() -> (
    AsyncGenerator[aind_session_json_service_async_client.DefaultApi, None]
):
    """
    Yield an aind_tars_service_async_client.DefaultApi object.
    """
    async with aind_session_json_service_async_client.ApiClient(
        tars_config
    ) as api_client:
        api_instance = aind_session_json_service_async_client.DefaultApi(
            api_client
        )
        yield api_instance
