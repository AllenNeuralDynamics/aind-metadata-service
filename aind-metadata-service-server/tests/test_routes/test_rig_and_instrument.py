"""Test instrument routes"""

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from requests import HTTPError, Response

TEST_DIR = Path(__file__).parent / ".."
TEST_INSTRUMENT_JSON = (
    TEST_DIR / "resources" / "slims" / "instrument_example.json"
)


class TestRoute:
    """Test responses."""

    @patch("aind_metadata_service_server.routes.rig_and_instrument.to_thread")
    def test_get_instrument(
        self,
        mock_to_thread: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response from DocDB"""
        with open(TEST_INSTRUMENT_JSON) as f:
            instrument_data = json.load(f)
        mocked_docdb_record = deepcopy(instrument_data)
        mock_to_thread.return_value = [mocked_docdb_record]
        response = client.get(
            "/api/v2/instrument/440_SmartSPIM1_20240327?partial_match=True"
        )

        assert 400 == response.status_code
        assert (
            "Models have not been validated."
            == response.headers["X-Error-Message"]
        )

    @patch("aind_metadata_service_server.routes.rig_and_instrument.to_thread")
    def test_get_instrument_not_found(
        self,
        mock_to_thread: AsyncMock,
        client: TestClient,
    ):
        """Tests 404 response when instrument is not found in DocDB"""
        mock_to_thread.return_value = []

        response = client.get("/api/v2/instrument/nonexistent_instrument")

        assert 404 == response.status_code
        assert response.json()["detail"] == "Not found"

    @patch(
        "aind_metadata_service_server.routes.rig_and_instrument.DocDBClient"
        ".insert_one_docdb_record"
    )
    def test_post_instrument_success(
        self,
        mock_docdb_client_insert: MagicMock,
        client: TestClient,
    ):
        """Tests success post response for an instrument"""
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = json.dumps({"message": "success"}).encode(
            "utf-8"
        )
        mock_docdb_client_insert.return_value = mock_response
        body = {"instrument_id": "abc", "modification_date": "2025-10-10"}
        response = client.post("/api/v2/instrument", json=body)
        mock_docdb_client_insert.assert_called_once_with(
            {
                "instrument_id": "abc",
                "modification_date": "2025-10-10",
                "_id": "e9851dd4-297a-4fc6-91ec-5665823326a5",
            },
        )
        assert 200 == response.status_code
        assert response.json() == {"message": "success"}

    @patch(
        "aind_metadata_service_server.routes.rig_and_instrument.DocDBClient"
        ".delete_one_record"
    )
    @patch(
        "aind_metadata_service_server.routes.rig_and_instrument.DocDBClient"
        ".insert_one_docdb_record"
    )
    def test_post_replace_instrument_success(
        self,
        mock_docdb_client_insert_one: MagicMock,
        mock_docdb_client_delete_one: MagicMock,
        client: TestClient,
    ):
        """Tests success post response for an instrument with replace True"""
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = json.dumps({"message": "success"}).encode(
            "utf-8"
        )
        mock_docdb_client_delete_one.return_value = mock_response
        mock_docdb_client_insert_one.return_value = mock_response
        body = {"instrument_id": "abc", "modification_date": "2025-10-10"}
        response = client.post(
            "/api/v2/instrument", json=body, params={"replace": True}
        )
        mock_docdb_client_delete_one.assert_called_once_with(
            "e9851dd4-297a-4fc6-91ec-5665823326a5"
        )
        mock_docdb_client_insert_one.assert_called_once_with(
            {
                "instrument_id": "abc",
                "modification_date": "2025-10-10",
                "_id": "e9851dd4-297a-4fc6-91ec-5665823326a5",
            },
        )
        assert 200 == response.status_code
        assert response.json() == {"message": "success"}

    @patch(
        "aind_metadata_service_server.routes.rig_and_instrument.DocDBClient"
        ".insert_one_docdb_record"
    )
    def test_post_instrument_failure(
        self,
        mock_docdb_client_insert: MagicMock,
        client: TestClient,
    ):
        """Tests failed post response for an instrument missing id"""
        body = {"field1": "abc"}
        response = client.post("/api/v2/instrument", json=body)
        mock_docdb_client_insert.assert_not_called()
        assert 406 == response.status_code
        assert response.json() == {"message": "Missing instrument_id."}

    @patch(
        "aind_metadata_service_server.routes.rig_and_instrument.DocDBClient"
        ".insert_one_docdb_record"
    )
    def test_post_instrument_failure_missing_date(
        self,
        mock_docdb_client_insert: MagicMock,
        client: TestClient,
    ):
        """Tests failed post response for an instrument missing date"""
        body = {"instrument_id": "abc"}
        response = client.post("/api/v2/instrument", json=body)
        mock_docdb_client_insert.assert_not_called()
        assert 406 == response.status_code
        assert response.json() == {"message": "Missing modification_date."}

    @patch(
        "aind_metadata_service_server.routes.rig_and_instrument.DocDBClient"
        ".insert_one_docdb_record"
    )
    def test_post_instrument_failure_id_exists(
        self,
        mock_docdb_client_insert: MagicMock,
        client: TestClient,
    ):
        """Tests failed post response for an instrument same id"""
        mock_response = HTTPError(response=Response())
        mock_response.response._content = "duplicate key error".encode()
        mock_docdb_client_insert.side_effect = mock_response
        body = {"instrument_id": "abc", "modification_date": "2025-10-10"}
        response = client.post("/api/v2/instrument", json=body)
        mock_docdb_client_insert.assert_called_once_with(
            {
                "instrument_id": "abc",
                "modification_date": "2025-10-10",
                "_id": "e9851dd4-297a-4fc6-91ec-5665823326a5",
            },
        )
        assert 400 == response.status_code

    @patch(
        "aind_metadata_service_server.routes.rig_and_instrument.DocDBClient"
        ".insert_one_docdb_record"
    )
    def test_post_instrument_failure_server_error(
        self,
        mock_docdb_client_insert: MagicMock,
        client: TestClient,
    ):
        """Tests failed post response with server error"""
        mock_response = HTTPError(response=Response())
        mock_response.response._content = "Error".encode()
        mock_docdb_client_insert.side_effect = mock_response
        body = {"instrument_id": "abc", "modification_date": "2025-10-10"}
        response = client.post("/api/v2/instrument", json=body)
        mock_docdb_client_insert.assert_called_once_with(
            {
                "instrument_id": "abc",
                "modification_date": "2025-10-10",
                "_id": "e9851dd4-297a-4fc6-91ec-5665823326a5",
            },
        )
        assert 500 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
