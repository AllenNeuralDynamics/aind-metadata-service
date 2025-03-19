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

    def test_client_initialization(self) -> None:
        """Tests client initialization options"""

        # Test with required domain parameter
        client = AindMetadataServiceClient(domain="http://test-domain")
        self.assertEqual(client.domain, "http://test-domain")

        # Test with no domain (should raise error)
        with self.assertRaises(TypeError) as e:
            AindMetadataServiceClient()
        self.assertIn("You must specify the server domain.", str(e.exception))

        # Test with empty domain
        client = AindMetadataServiceClient(domain="")

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

    @mock.patch("requests.get")
    def test_get_intended_measurements(self, mock_get: MagicMock) -> None:
        """Tests the get_intended_measurements method"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": ['
            b'{"fiber_name": "Fiber_0", '
            b'"intended_measurement_R": "acetylcholine", '
            b'"intended_measurement_G": "dopamine", '
            b'"intended_measurement_B": "GABA", '
            b'"intended_measurement_Iso": "control"}'
            b"]}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_intended_measurements(mock_subject_id)

        mock_get.assert_has_calls(
            [
                call("some_url/intended_measurements/00000", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_injection_materials(self, mock_get: MagicMock) -> None:
        """Tests the get_injection_materials method"""

        mock_prep_lot_number = "VT123"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": {'
            b'"prep_lot_number": "VT123", '
            b'"viral_titer": "2.5e12", '
            b'"material_type": "AAV"'
            b"}}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_injection_materials(mock_prep_lot_number)

        mock_get.assert_has_calls(
            [
                call("some_url/tars_injection_materials/VT123", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_ecephys_sessions(self, mock_get: MagicMock) -> None:
        """Tests the get_ecephys_sessions method"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": ['
            b'{"session_id": "123", "subject_id": "00000", '
            b'"session_start_time": "2023-01-01T12:00:00", '
            b'"session_type": "ephys"}'
            b"]}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_ecephys_sessions(mock_subject_id)

        mock_get.assert_has_calls(
            [
                call("some_url/ecephys_sessions_by_subject/00000", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_protocols(self, mock_get: MagicMock) -> None:
        """Tests the get_protocols method"""

        mock_protocol_name = "Protocol-123"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": {'
            b'"protocol_name": "Protocol-123", '
            b'"protocol_type": "Behavior", '
            b'"version": "1.0"'
            b"}}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_protocols(mock_protocol_name)

        mock_get.assert_has_calls(
            [
                call("some_url/protocols/Protocol-123", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_mgi_allele(self, mock_get: MagicMock) -> None:
        """Tests the get_mgi_allele method"""

        mock_allele_name = "Allele1"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": {'
            b'"allele_name": "Allele1", '
            b'"allele_symbol": "All1", '
            b'"allele_type": "Targeted"'
            b"}}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_mgi_allele(mock_allele_name)

        mock_get.assert_has_calls(
            [
                call("some_url/mgi_allele/Allele1", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_perfusions(self, mock_get: MagicMock) -> None:
        """Tests the get_perfusions method"""

        mock_subject_id = "00000"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": {'
            b'"subject_id": "00000", '
            b'"perfusion_date": "2023-01-15", '
            b'"perfusion_method": "Standard"'
            b"}}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_perfusions(mock_subject_id)

        mock_get.assert_has_calls(
            [
                call("some_url/perfusions/00000", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_funding(self, mock_get: MagicMock) -> None:
        """Tests the get_funding method"""

        mock_project_name = "Project-ABC"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": {'
            b'"project_name": "Project-ABC", '
            b'"funding_source": "NIH", '
            b'"grant_id": "R01-123456"'
            b"}}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_funding(mock_project_name)

        mock_get.assert_has_calls(
            [
                call("some_url/funding/Project-ABC", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_smartspim_imaging(self, mock_get: MagicMock) -> None:
        """Tests the get_smartspim_imaging method with parameters"""

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": {'
            b'"data": "test imaging data"'
            b"}}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        # Test with parameters
        response = ams_client.get_smartspim_imaging(
            subject_id="123456",
            start_date_gte="2023-01-01",
            end_date_lte="2023-12-31",
        )

        mock_get.assert_has_calls(
            [
                call(
                    "some_url/slims/smartspim_imaging",
                    params={
                        "subject_id": "123456",
                        "start_date_gte": "2023-01-01",
                        "end_date_lte": "2023-12-31",
                    },
                ),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_histology(self, mock_get: MagicMock) -> None:
        """Tests the get_histology method with parameters"""

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": {'
            b'"histology_data": "sample histology data"'
            b"}}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        # Test with parameters
        response = ams_client.get_histology(
            subject_id="123456",
            start_date_gte="2023-01-01",
            end_date_lte="2023-12-31",
        )

        mock_get.assert_has_calls(
            [
                call(
                    "some_url/slims/histology",
                    params={
                        "subject_id": "123456",
                        "start_date_gte": "2023-01-01",
                        "end_date_lte": "2023-12-31",
                    },
                ),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())

    @mock.patch("requests.get")
    def test_get_project_names(self, mock_get: MagicMock) -> None:
        """Tests the get_project_names method"""

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'{"status_code": 200, "message": "Success", "data": ['
            b'"Project-A", "Project-B", "Project-C"'
            b"]}"
        )

        mock_get.return_value.__enter__.return_value = mock_response

        ams_client = AindMetadataServiceClient(domain="some_url")

        response = ams_client.get_project_names()

        mock_get.assert_has_calls(
            [
                call("some_url/project_names", params={}),
                call().__enter__(),
                call().__exit__(None, None, None),
            ]
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response.json(), response.json())


if __name__ == "__main__":
    unittest.main()
