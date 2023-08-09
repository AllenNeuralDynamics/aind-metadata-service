"""Module to test the aind_metadata_service client."""
import json
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
        mock_response.status_code = 200
        mock_response._content = json.dumps(
            {
                "message": "Valid Model.",
                "data": {
                    "describedBy": "https://acme.com/subject.py",
                    "schema_version": "0.2.2",
                    "species": "Mus musculus",
                    "subject_id": mock_subject_id,
                    "sex": "Female",
                    "date_of_birth": "2022-05-01",
                    "genotype": "wt/wt",
                    "mgi_allele_ids": None,
                    "background_strain": None,
                    "source": None,
                    "rrid": None,
                    "restrictions": None,
                    "breeding_group": "breeding_group_id",
                    "maternal_id": "00001",
                    "maternal_genotype": "wt/wt",
                    "paternal_id": "00002",
                    "paternal_genotype": "wt/wt",
                    "light_cycle": None,
                    "home_cage_enrichment": None,
                    "wellness_reports": None,
                    "notes": None,
                },
            }
        ).encode("utf-8")

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
        mock_response.status_code = 200
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
            model_response.status_code,
            pickle.loads(response.content).status_code,
        )
        self.assertEqual(
            model_response.aind_models,
            pickle.loads(response.content).aind_models,
        )

    @mock.patch("requests.get")
    def test_get_procedures(self, mock_get: MagicMock) -> None:
        """Tests the get_procedures method with default pickle = False"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        mock_response.status_code = 418
        mock_response._content = json.dumps(
            {
                "message": "Validation Errors: 8 validation errors for "
                "Procedures\nheadframes\n  'NoneType' object is not "
                "iterable (type=type_error)\ncraniotomies\n  "
                "'NoneType' object is not iterable "
                "(type=type_error)\nmri_scans\n  'NoneType' object is "
                "not iterable (type=type_error)\ninjections\n  "
                "'NoneType' object is not iterable "
                "(type=type_error)\nfiber_implants\n  "
                "'NoneType' object is not iterable "
                "(type=type_error)\ntraining_protocols\n  "
                "'NoneType' object is not iterable "
                "(type=type_error)\ntissue_preparations\n  "
                "'NoneType' object is not iterable "
                "(type=type_error)\nother_procedures\n  "
                "'NoneType' object is not iterable (type=type_error)",
                "data": {
                    "describedBy": "https://acme.com/procedures.py",
                    "schema_version": "0.4.4",
                    "subject_id": mock_subject_id,
                    "headframes": None,
                    "craniotomies": None,
                    "mri_scans": None,
                    "injections": None,
                    "fiber_implants": None,
                    "water_restriction": None,
                    "training_protocols": None,
                    "tissue_preparations": None,
                    "other_procedures": None,
                    "notes": None,
                },
            }
        ).encode("utf-8")

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

        self.assertEqual(418, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_procedures_pickled(self, mock_get: MagicMock) -> None:
        """Tests the get_procedures method with pickle = True"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        mock_response.status_code = 418
        model = Procedures.construct(subject_id=mock_subject_id)
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
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

        self.assertEqual(418, response.status_code)
        self.assertEqual(
            model_response.status_code,
            pickle.loads(response.content).status_code,
        )
        self.assertEqual(
            model_response.aind_models,
            pickle.loads(response.content).aind_models,
        )


if __name__ == "__main__":
    unittest.main()
