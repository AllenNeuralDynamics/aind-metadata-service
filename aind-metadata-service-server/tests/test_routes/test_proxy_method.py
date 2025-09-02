"""Tests server module and proxy method."""

import unittest
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient, RequestError, Response
from starlette.requests import Request

from aind_metadata_service_server.routes.v1_proxy import proxy


class TestProxyServer(unittest.IsolatedAsyncioTestCase):
    """Tests proxy server that handles v1 routes."""

    @patch("httpx.AsyncClient.request")
    @patch("fastapi.Request.body")
    async def test_proxy(
        self,
        mock_request_body: AsyncMock,
        mock_async_client_request: AsyncMock,
    ):
        """Tests proxy method."""
        mock_request_body.return_value = {"foo": "bar"}
        mock_response = Response(200)
        mock_async_client_request.return_value = mock_response

        response = await proxy(
            request=Request(
                scope={"type": "http", "headers": dict(), "method": "POST"}
            ),
            async_client=AsyncClient(),
            path="/foo",
        )
        self.assertEqual(200, response.status_code)

    @patch("httpx.AsyncClient.request")
    @patch("fastapi.Request.body")
    async def test_proxy_with_error(
        self,
        mock_request_body: AsyncMock,
        mock_async_client_request: AsyncMock,
    ):
        """Tests proxy method when an error occurs."""
        mock_request_body.return_value = {"foo": "bar"}
        mock_async_client_request.side_effect = RequestError("Error!")

        response = await proxy(
            request=Request(
                scope={"type": "http", "headers": dict(), "method": "POST"}
            ),
            async_client=AsyncClient(),
            path="/foo",
        )
        self.assertEqual(500, response.status_code)


if __name__ == "__main__":
    unittest.main()
