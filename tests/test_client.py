"""Module to test the aind_metadata_service client."""

import unittest
from datetime import date
from unittest import mock
from unittest.mock import MagicMock, call

import requests
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.core.subject import (
    BackgroundStrain,
    BreedingInfo,
    Housing,
    Sex,
    Species,
    Subject,
)
from aind_data_schema_models.organizations import Organization

from aind_metadata_service.client import AindMetadataServiceClient
from aind_metadata_service.response_handler import ModelResponse, StatusCodes


class TestAindMetadataServiceClient(unittest.TestCase):
    """Tests the AindMetadataServiceClient class methods"""

    @mock.patch("requests.get")
    def test_get_subject(self, mock_get: MagicMock) -> None:
        """Tests the get_subject method"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        model = Subject(
            species=Species.MUS_MUSCULUS,
            breeding_info=BreedingInfo(
                breeding_group="breeding_group_id",
                maternal_id="00001",
                maternal_genotype="wt/wt",
                paternal_id="00002",
                paternal_genotype="wt/wt",
            ),
            subject_id=mock_subject_id,
            sex=Sex.FEMALE,
            source=Organization.AI,
            date_of_birth=date(2022, 5, 1),
            genotype="wt/wt",
            alleles=[],
            background_strain=BackgroundStrain.C57BL_6J,
            housing=Housing(),
            rrid=None,
            restrictions=None,
            wellness_reports=[],
            notes=None,
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
                call("some_url/subject/00000", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_procedures(self, mock_get: MagicMock) -> None:
        """Tests the get_procedures method"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        model = Procedures.model_construct(subject_id=mock_subject_id)
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
                call("some_url/procedures/00000", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())


if __name__ == "__main__":
    unittest.main()
