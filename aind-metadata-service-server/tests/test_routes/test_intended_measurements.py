"""Tests intended measurements route"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from aind_sharepoint_service_async_client.models.nsb2023_list import (
    NSB2023List,
)
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).parent / ".."
EXAMPLE_NSB2023_JSON = (
    TEST_DIR / "resources" / "nsb2023" / "nsb2023_intended_measurements.json"
)


class TestRoute:
    """Test responses."""

    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    def test_get_intended_measurements_success(
        self,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        client: TestClient,
    ):
        """Tests successful retrieval of intended measurements."""
        with open(EXAMPLE_NSB2023_JSON) as f:
            contents = json.load(f)
        mock_nsb2023.return_value = [NSB2023List.model_validate(contents)]
        mock_nsb_present.return_value = []

        response = client.get("/intended_measurements/000000")
        assert response.status_code == 300


if __name__ == "__main__":
    pytest.main([__file__])
