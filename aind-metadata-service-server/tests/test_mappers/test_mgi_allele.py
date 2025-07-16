"""Tests methods in mapping module"""

import unittest
from copy import deepcopy
from unittest.mock import patch
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.registries import Registry
from aind_mgi_service_async_client.models import MgiSummaryRow

from aind_metadata_service_server.mappers.mgi_allele import MgiMapper


class TestMgiMapping(unittest.TestCase):
    """Class to test methods for MgiMapping"""

    def setUp(self):
        """Set up base test data with a single MgiSummaryRow object"""
        self.base_summary_row = MgiSummaryRow(
            detail_uri="/allele/MGI:5558086",
            feature_type="Targeted allele",
            strand=None,
            chromosome="9",
            stars="****",
            best_match_text="Ai93",
            best_match_type="Synonym",
            name=("intergenic site 7; " "targeted mutation 93, Hongkui Zeng"),
            location="syntenic",
            symbol="Igs7<tm93.1(tetO-GCaMP6f)Hze>",
        )

    def test_map_to_aind_pid_name_success(self):
        """Tests successful mapping of MGI summary row to PIDName"""
        mapper = MgiMapper(mgi_summary_row=self.base_summary_row)
        pid_name = mapper.map_to_aind_pid_name()

        expected_response = PIDName(
            name="Igs7<tm93.1(tetO-GCaMP6f)Hze>",
            abbreviation=None,
            registry=Registry.MGI,
            registry_identifier="5558086",
        )

        self.assertEqual(expected_response, pid_name)

    def test_map_to_aind_pid_name_not_exact_match(self):
        """Tests mapping when stars indicate not an exact match"""
        row = deepcopy(self.base_summary_row)
        row.stars = "**"

        mapper = MgiMapper(mgi_summary_row=row)
        pid_name = mapper.map_to_aind_pid_name()

        self.assertIsNone(pid_name)

    def test_map_to_aind_pid_name_wrong_match_type(self):
        """Tests mapping when best_match_type is not 'Synonym'"""
        row = deepcopy(self.base_summary_row)
        row.best_match_type = "Gene"

        mapper = MgiMapper(mgi_summary_row=row)
        pid_name = mapper.map_to_aind_pid_name()

        self.assertIsNone(pid_name)

    def test_map_to_aind_pid_name_no_identifier(self):
        """Tests mapping when no identifier can be extracted"""
        row = deepcopy(self.base_summary_row)
        row.detail_uri = ""

        mapper = MgiMapper(mgi_summary_row=row)
        pid_name = mapper.map_to_aind_pid_name()

        expected_response = PIDName(
            name="Igs7<tm93.1(tetO-GCaMP6f)Hze>",
            abbreviation=None,
            registry=Registry.MGI,
            registry_identifier=None,
        )

        self.assertEqual(expected_response, pid_name)

    def test_map_to_aind_pid_name_no_symbol(self):
        """Tests mapping when no symbol is provided"""
        row = deepcopy(self.base_summary_row)
        row.symbol = None

        mapper = MgiMapper(mgi_summary_row=row)
        pid_name = mapper.map_to_aind_pid_name()

        self.assertIsNone(pid_name)

    def test_map_to_aind_pid_name_malformed_detail_uri(self):
        """Tests mapping when detail URI doesn't match expected pattern"""
        row = deepcopy(self.base_summary_row)
        row.detail_uri = "/something/else/123"

        mapper = MgiMapper(mgi_summary_row=row)
        pid_name = mapper.map_to_aind_pid_name()

        expected_response = PIDName(
            name="Igs7<tm93.1(tetO-GCaMP6f)Hze>",
            abbreviation=None,
            registry=Registry.MGI,
            registry_identifier=None,
        )

        self.assertEqual(expected_response, pid_name)

    def test_detail_uri_pattern_extraction(self):
        """Tests the regex pattern for extracting MGI identifiers"""
        valid_uris = [
            "/allele/MGI:5558086",
            "/allele/MGI:123456",
            "/allele/MGI:1",
        ]

        for uri in valid_uris:
            match = MgiMapper.DETAIL_URI_PATTERN.match(uri)
            self.assertIsNotNone(match)
            self.assertTrue(match.group(1).isdigit())

        invalid_uris = [
            "/gene/MGI:5558086",
            "/allele/ABC:5558086",
            "/allele/MGI:",
            "/allele/MGI:abc",
            "",
        ]

        for uri in invalid_uris:
            match = MgiMapper.DETAIL_URI_PATTERN.match(uri)
            self.assertIsNone(match)

    def test_map_to_aind_pid_name_validation_error(self):
        """Tests mapping when PIDName validation fails"""
        row = deepcopy(self.base_summary_row)
        mapper = MgiMapper(mgi_summary_row=row)
        with patch(
            "aind_metadata_service_server.mappers.mgi_allele.Registry"
        ) as mock_registry:
            mock_registry.MGI = 123

            with self.assertLogs(level="WARNING") as captured:
                pid_name = mapper.map_to_aind_pid_name()

            self.assertIn(
                "Validation error creating PIDName model", captured.output[0]
            )
            self.assertIsInstance(pid_name, PIDName)


if __name__ == "__main__":
    unittest.main()
