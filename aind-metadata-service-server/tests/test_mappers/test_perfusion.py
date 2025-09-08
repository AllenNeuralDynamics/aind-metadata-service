"""Tests methods in perfusion mapper module"""

import unittest
from datetime import date
from decimal import Decimal

from aind_data_schema.components.surgery_procedures import Perfusion
from aind_data_schema.core.procedures import Surgery
from aind_smartsheet_service_async_client.models import PerfusionsModel

from aind_metadata_service_server.mappers.perfusion import PerfusionMapper


class TestPerfusionMapper(unittest.TestCase):
    """Class to test methods for PerfusionMapper."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        cls.perfusions_sheet = [
            PerfusionsModel(
                subject_id="689418.0",
                var_date=date(2023, 10, 2),
                experimenter="Person S",
                iacuc_protocol=(
                    "2109 - Analysis of brain - wide neural circuits in the"
                    " mouse"
                ),
                animal_weight_prior__g="22.0",
                output_specimen_id_s="689418.0",
                postfix_solution="1xPBS",
                notes="Good",
            ),
            PerfusionsModel(
                subject_id="689418.0",
                var_date=None,
                experimenter="Person S",
                iacuc_protocol=None,
                animal_weight_prior__g="22.0",
                output_specimen_id_s="689418.0",
                postfix_solution="1xPBS",
                notes="Good",
            ),
            PerfusionsModel(
                subject_id="689418.0",
                var_date=date(2023, 10, 2),
                experimenter="Person S",
                iacuc_protocol="abc",  # Malformed IACUC
                animal_weight_prior__g="22.0",
                output_specimen_id_s="689418.0",
                postfix_solution="1xPBS",
                notes="Good",
            ),
        ]

        cls.expected_surgery_model = Surgery.model_construct(
            start_date=date(2023, 10, 2),
            experimenters=["Person S"],
            ethics_review_id="2109",
            animal_weight_prior=Decimal("22.0"),
            animal_weight_post=None,
            anaesthesia=None,
            notes="Good",
            procedures=[
                Perfusion(
                    output_specimen_ids={"689418"},
                    protocol_id="dx.doi.org/10.17504/protocols.io.bg5vjy66",
                )
            ],
        )

    def test_mapping_success(self):
        """Tests successful mapping of perfusion data"""
        mapper = PerfusionMapper(smartsheet_perfusion=self.perfusions_sheet[0])
        surgery_model = mapper.map_to_aind_surgery()
        self.assertEqual(self.expected_surgery_model, surgery_model)

    def test_mapping_missing_iacuc_id_and_date(self):
        """Tests response when iacuc field is missing"""
        mapper = PerfusionMapper(smartsheet_perfusion=self.perfusions_sheet[1])
        surgery_model = mapper.map_to_aind_surgery()

        self.assertIsNone(surgery_model.ethics_review_id)
        self.assertIsNone(surgery_model.start_date)

    def test_mapping_malformed_iacuc_id(self):
        """Tests mapping when the iacuc field is malformed"""
        mapper = PerfusionMapper(smartsheet_perfusion=self.perfusions_sheet[2])
        surgery_model = mapper.map_to_aind_surgery()

        self.assertEqual("abc", surgery_model.ethics_review_id)


if __name__ == "__main__":
    unittest.main()
