"""Tests mapper module"""

import unittest
from datetime import date
from decimal import Decimal

from aind_data_schema.core.procedures import Perfusion, Surgery

from aind_metadata_service.backends.smartsheet.models import PerfusionsModel
from aind_metadata_service.routers.perfusions.mapper import Mapper


class TestMapper(unittest.TestCase):
    """Tests methods in Mapper class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up class with example data."""
        cls.mapper = Mapper(
            perfusions_model=PerfusionsModel(
                subject_id=Decimal("689418.0"),
                date=date(2023, 10, 2),
                experimenter="Jane Smith",
                iacuc_protocol=(
                    "2109 - Analysis of brain "
                    "- wide neural circuits in the mouse"
                ),
                animal_weight_prior=Decimal("22.0"),
                output_specimen_id=Decimal("689418.0"),
                postfix_solution="1xPBS",
                notes="Good",
            )
        )

    def test_map_iacuc_protocol(self):
        """Tests _map_iacuc_protocol with matched regex pattern"""

        protocol_id = self.mapper._map_iacuc_protocol(
            iacuc_protocol_id=(
                "2109 - Analysis of brain - wide neural circuits in the mouse"
            )
        )
        self.assertEqual("2109", protocol_id)

    def test_map_iacuc_protocol_none(self):
        """Tests _map_iacuc_protocol when None passed into arg"""

        protocol_id = self.mapper._map_iacuc_protocol(iacuc_protocol_id=None)
        self.assertIsNone(protocol_id)

    def test_map_iacuc_protocol_no_match(self):
        """Tests _map_iacuc_protocol when regex is not matched"""

        protocol_id = self.mapper._map_iacuc_protocol(
            iacuc_protocol_id="abc-123"
        )
        self.assertEqual("abc-123", protocol_id)

    def test_map_to_perfusions_valid(self):
        """Tests map to perfusions method when a valid model is returned"""
        mapped_model = self.mapper.map_to_perfusions()
        expected_mapped_model = Surgery(
            procedure_type="Surgery",
            protocol_id="dx.doi.org/10.17504/protocols.io.bg5vjy66",
            start_date=date(2023, 10, 2),
            experimenter_full_name="Jane Smith",
            iacuc_protocol="2109",
            animal_weight_prior=Decimal("22.0"),
            animal_weight_post=None,
            anaesthesia=None,
            workstation_id=None,
            procedures=[
                Perfusion(
                    procedure_type="Perfusion",
                    protocol_id="dx.doi.org/10.17504/protocols.io.bg5vjy66",
                    output_specimen_ids={"689418"},
                )
            ],
            notes=None,
        )
        self.assertEqual(expected_mapped_model, mapped_model)


if __name__ == "__main__":
    unittest.main()
