"""Module to test the aind_metadata_service client."""
import pickle
import unittest
from unittest import mock
from unittest.mock import MagicMock, call

import requests
from aind_data_schema.procedures import Procedures
from aind_data_schema.subject import Species, Subject

from aind_metadata_service.client import AindMetadataServiceClient
from aind_metadata_service.response_handler import ModelResponse, StatusCodes


class TestAindMetadataServiceClient(unittest.TestCase):
    """Tests the AindMetadataServiceClient class methods"""

    @mock.patch("requests.get")
    def test_get_subject(self, mock_get: MagicMock) -> None:
        """Tests the get_subject method with default pickle = False."""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        model = Subject(
            species=Species.MUS_MUSCULUS,
            subject_id=mock_subject_id,
            sex="Female",
            date_of_birth="2022-05-01",
            genotype="wt/wt",
            breeding_group="breeding_group_id",
            maternal_id="00001",
            maternal_genotype="wt/wt",
            paternal_id="00002",
            paternal_genotype="wt/wt",
        )
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        mock_response.status_code = (
            model_response.map_to_json_response().status_code
        )
        mock_response._content = model_response.map_to_json_response().body

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_subject(mock_subject_id)

        mock_get.assert_has_calls(
            [
                call("some_url/subject/00000", params={"pickle": False}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_subject_pickled(self, mock_get: MagicMock) -> None:
        """Tests the get_subject method with pickle = True."""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        model = Subject(
            species=Species.MUS_MUSCULUS,
            subject_id=mock_subject_id,
            sex="Female",
            date_of_birth="2022-05-01",
            genotype="wt/wt",
            breeding_group="breeding_group_id",
            maternal_id="00001",
            maternal_genotype="wt/wt",
            paternal_id="00002",
            paternal_genotype="wt/wt",
        )
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        mock_response.status_code = (
            model_response.map_to_pickled_response().status_code
        )
        mock_response._content = model_response.map_to_pickled_response().body

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_subject(mock_subject_id, pickle=True)

        mock_get.assert_has_calls(
            [
                call("some_url/subject/00000", params={"pickle": True}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            model,
            pickle.loads(response.content),
        )

    @mock.patch("requests.get")
    def test_get_procedures(self, mock_get: MagicMock) -> None:
        """Tests the get_procedures method with default pickle = False"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        model = Procedures.construct(subject_id=mock_subject_id)
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        mock_response.status_code = (
            model_response.map_to_json_response().status_code
        )
        mock_response._content = model_response.map_to_json_response().body

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_procedures(mock_subject_id)

        mock_get.assert_has_calls(
            [
                call("some_url/procedures/00000", params={"pickle": False}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_procedures_pickled(self, mock_get: MagicMock) -> None:
        """Tests the get_procedures method with pickle = True"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        model = Procedures.construct(subject_id=mock_subject_id)
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        mock_response.status_code = (
            model_response.map_to_pickled_response().status_code
        )
        mock_response._content = model_response.map_to_pickled_response().body

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_procedures(mock_subject_id, pickle=True)

        mock_get.assert_has_calls(
            [
                call("some_url/procedures/00000", params={"pickle": True}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            model,
            pickle.loads(response.content),
        )


if __name__ == "__main__":
    unittest.main()
