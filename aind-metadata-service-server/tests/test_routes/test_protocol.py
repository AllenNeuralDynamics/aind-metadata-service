"""Test protocol routes"""

from unittest.mock import AsyncMock, patch

import pytest
from aind_smartsheet_service_async_client.models import ProtocolsModel
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    def test_get_protocols(
        self,
        mock_get_protocols: AsyncMock,
        client: TestClient,
    ):
        """Tests successful protocol retrieval"""
        mock_get_protocols.return_value = [
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Tetrahydrofuran and Dichloromethane Delipidation of a "
                    "Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
                version="1.0",
            ),
        ]
        response = client.get(
            "/api/v2/protocols/Tetrahydrofuran and Dichloromethane"
            " Delipidation of a Whole Mouse Brain"
        )
        assert 200 == response.status_code
        assert 1 == len(mock_get_protocols.mock_calls)
        mock_get_protocols.assert_called_once_with(
            protocol_name=(
                "Tetrahydrofuran and Dichloromethane Delipidation"
                " of a Whole Mouse Brain"
            ),
            _request_timeout=10,
        )

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    def test_get_protocols_not_found(
        self,
        mock_get_protocols: AsyncMock,
        client: TestClient,
    ):
        """Tests protocol not found scenario"""
        mock_get_protocols.return_value = []
        response = client.get("/api/v2/protocols/Nonexistent Protocol Name")
        assert 404 == response.status_code
        assert 1 == len(mock_get_protocols.mock_calls)
        mock_get_protocols.assert_called_once_with(
            protocol_name="Nonexistent Protocol Name",
            _request_timeout=10,
        )

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    def test_get_protocols_multiple_found(
        self,
        mock_get_protocols: AsyncMock,
        client: TestClient,
    ):
        """Tests multiple protocols found scenario"""
        mock_get_protocols.return_value = [
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Tetrahydrofuran and Dichloromethane Delipidation of a "
                    "Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
                version="1.0",
            ),
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Tetrahydrofuran and Dichloromethane Delipidation of a "
                    "Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
                version="2.0",
            ),
        ]
        response = client.get(
            "/api/v2/protocols/Tetrahydrofuran and Dichloromethane"
            " Delipidation of a Whole Mouse Brain"
        )
        assert 500 == response.status_code
        assert 1 == len(mock_get_protocols.mock_calls)
        mock_get_protocols.assert_called_once_with(
            protocol_name=(
                "Tetrahydrofuran and Dichloromethane Delipidation"
                " of a Whole Mouse Brain"
            ),
            _request_timeout=10,
        )

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    def test_get_protocols_with_collection(
        self,
        mock_get_protocols: AsyncMock,
        client: TestClient,
    ):
        """Tests successful protocol retrieval with protocol_collection=True"""
        mock_get_protocols.return_value = [
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Perfusion",
                protocol_name=(
                    "Protocol Collection: Perfusing, Sectioning, IHC, "
                    "Mounting and Coverslipping Mouse Brain Specimens"
                ),
                doi="dx.doi.org/10.17504/protocols.io.kxygx3yxkg8j/v1",
                version="1.0",
                protocol_collection=True,
            ),
        ]
        response = client.get(
            "/api/v2/protocols/Protocol Collection: Perfusing, Sectioning, "
            "IHC, Mounting and Coverslipping Mouse Brain Specimens"
        )
        assert 200 == response.status_code
        assert 1 == len(mock_get_protocols.mock_calls)
        # Verify protocol_collection is boolean in response
        response_data = response.json()
        assert response_data["protocol_collection"] is True


if __name__ == "__main__":
    pytest.main([__file__])
