"""Module to test main app"""

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from aind_metadata_service_server.main import routers


class TestMain:
    """Tests app endpoints"""

    def test_get_healthcheck(self, client: TestClient):
        """Tests healthcheck"""
        response = client.get("/api/v2/healthcheck")
        assert 200 == response.status_code

    def test_operation_ids_are_set(self, client: TestClient):
        """Test that operation_id is set to route name for all APIRoutes."""
        # Collect all API routes from all routers
        all_api_routes = []
        for router in routers:
            api_routes = [r for r in router.routes if isinstance(r, APIRoute)]
            all_api_routes.extend(api_routes)

        assert len(all_api_routes) > 0
        assert all(r.operation_id == r.name for r in all_api_routes)


if __name__ == "__main__":
    pytest.main([__file__])
