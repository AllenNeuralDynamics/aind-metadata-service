"""Tests methods in mapping module"""

import unittest
from unittest.mock import MagicMock, patch

from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.registries import Registry

from aind_metadata_service.mgi.client import MgiResponse
from aind_metadata_service.mgi.mapping import MgiMapper
from aind_metadata_service.response_handler import ModelResponse


class TestMgiMapping(unittest.TestCase):
    """Class to test methods for MgiMapping"""

    @classmethod
    def setUpClass(cls):
        """Set up class with examples"""

        example_response = {
            "summaryRows": [
                {
                    "detailUri": "/allele/MGI:5558086",
                    "featureType": "Targeted allele",
                    "strand": None,
                    "chromosome": "9",
                    "stars": "****",
                    "bestMatchText": "Ai93",
                    "bestMatchType": "Synonym",
                    "name": (
                        "intergenic site 7; "
                        "targeted mutation 93, Hongkui Zeng"
                    ),
                    "location": "syntenic",
                    "symbol": "Igs7<tm93.1(tetO-GCaMP6f)Hze>",
                }
            ],
            "totalCount": 1,
            "meta": None,
        }
        cls.error_response = ModelResponse.internal_server_error_response()
        cls.example_response = MgiResponse(**example_response)

    def test_get_model_response_error_input(self):
        """Tests get_model_response method when an error response is passed"""

        mapper = MgiMapper(mgi_info=self.error_response)
        model_response = mapper.get_model_response()
        self.assertEqual(500, model_response.status_code.value)

    def test_get_model_response_empty_summary_rows(self):
        """Tests get_model_response method when no summary rows are returned"""

        mapper = MgiMapper(mgi_info=MgiResponse(summaryRows=[]))
        model_response = mapper.get_model_response()
        self.assertEqual(404, model_response.status_code.value)

    def test_get_model_response_not_exact_match(self):
        """Tests get_model_response method when no exact match returned"""

        example_response_json = self.example_response.model_dump_json()
        updated_response = MgiResponse.model_validate_json(
            example_response_json
        )
        updated_response.summaryRows[0].stars = "**"
        mapper = MgiMapper(mgi_info=updated_response)
        model_response = mapper.get_model_response()
        self.assertEqual(404, model_response.status_code.value)

    def test_get_model_response_no_identifier(self):
        """Tests get_model_response method when no identifier found"""

        example_response_json = self.example_response.model_dump_json()
        updated_response = MgiResponse.model_validate_json(
            example_response_json
        )
        updated_response.summaryRows[0].detailUri = ""
        mapper = MgiMapper(mgi_info=updated_response)
        model_response = mapper.get_model_response()
        expected_response = PIDName(
            name="Igs7<tm93.1(tetO-GCaMP6f)Hze>",
            abbreviation=None,
            registry=Registry.MGI,
            registry_identifier=None,
        )
        self.assertEqual(expected_response, model_response.aind_models[0])

    def test_get_model_response_success(self):
        """Tests get_model_response method success"""

        mapper = MgiMapper(mgi_info=self.example_response)
        model_response = mapper.get_model_response()
        expected_response = PIDName(
            name="Igs7<tm93.1(tetO-GCaMP6f)Hze>",
            abbreviation=None,
            registry=Registry.MGI,
            registry_identifier="5558086",
        )
        self.assertEqual(expected_response, model_response.aind_models[0])

    @patch("re.match")
    def test_get_model_response_error(self, mock_match: MagicMock):
        """Tests get_model_response method when an error occurs"""

        mock_match.side_effect = Exception("Something went wrong.")
        mapper = MgiMapper(mgi_info=self.example_response)
        with self.assertLogs(level="ERROR") as captured:
            model_response = mapper.get_model_response()

        self.assertIn("Something went wrong.", captured.output[0])
        self.assertEqual(500, model_response.status_code.value)


if __name__ == "__main__":
    unittest.main()
