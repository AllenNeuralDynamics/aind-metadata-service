"""Module to test TARS mapping."""

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from aind_data_schema.core.procedures import TarsVirusIdentifiers

from aind_metadata_service.tars.mapping import (
    PrepProtocols,
    TarsResponseHandler,
    ViralMaterial,
    ViralPrepAliases,
    ViralPrepTypes,
    VirusPrepType,
)


class TestTarsResponseHandler(unittest.TestCase):
    """Class to test methods of TarsResponseHandler"""

    def test_map_prep_type_and_protocol(self):
        """Tests that prep_type and protocol are mapped as expected."""
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.CRUDE_SOP.value
        )
        self.assertEqual(prep_type, VirusPrepType.CRUDE)
        self.assertEqual(prep_protocol, PrepProtocols.SOP_VC002.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.PURIFIED_SOP.value
        )
        self.assertEqual(prep_type, VirusPrepType.PURIFIED)
        self.assertEqual(prep_protocol, PrepProtocols.SOP_VC003.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.CRUDE_HGT.value
        )
        self.assertEqual(prep_type, VirusPrepType.CRUDE)
        self.assertEqual(prep_protocol, PrepProtocols.HGT.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.RABIES_SOP.value
        )
        self.assertIsNone(prep_type)
        self.assertEqual(prep_protocol, PrepProtocols.SOP_VC001.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.CRUDE_PHP_SOP.value
        )
        self.assertEqual(prep_type, VirusPrepType.CRUDE)
        self.assertEqual(prep_protocol, PrepProtocols.SOP_VC004.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.CRUDE_MGT2.value
        )
        self.assertEqual(prep_type, VirusPrepType.CRUDE)
        self.assertEqual(prep_protocol, PrepProtocols.MGT2.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.CRUDE_MGT1.value
        )
        self.assertEqual(prep_type, VirusPrepType.CRUDE)
        self.assertEqual(prep_protocol, PrepProtocols.MGT1.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.PURIFIED_MGT1.value
        )
        self.assertEqual(prep_type, VirusPrepType.PURIFIED)
        self.assertEqual(prep_protocol, PrepProtocols.MGT1.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.CRUDE_HGT1.value
        )
        self.assertEqual(prep_type, VirusPrepType.CRUDE)
        self.assertEqual(prep_protocol, PrepProtocols.HGT1.value)
        (
            prep_type,
            prep_protocol,
        ) = TarsResponseHandler._map_prep_type_and_protocol(
            ViralPrepTypes.UNKNOWN.value
        )
        self.assertIsNone(prep_type)
        self.assertIsNone(prep_protocol)

    @patch("logging.warning")
    def test_convert_datetime(self, mock_warn: MagicMock):
        """Tests that datetime is converted as expected."""
        valid_date = "2023-12-15T12:34:56Z"
        invalid_date = "12/15/2023"

        converted_date = TarsResponseHandler._convert_datetime(valid_date)
        self.assertIsInstance(converted_date, date)

        converted_invalid_date = TarsResponseHandler._convert_datetime(
            invalid_date
        )
        self.assertIsNone(converted_invalid_date)
        mock_warn.assert_called_once_with(
            "Invalid date format. Please provide a date in the format:"
            " YYYY-MM-DDTHH:MM:SSZ"
        )

    def test_map_virus_aliases(self):
        """Tests that aliases are mapped to fields as expected."""
        aliases = [
            {"name": "AiP123"},
            {"name": "AiV456"},
            {"name": "UnknownVirus"},
        ]

        viral_prep_aliases = TarsResponseHandler.map_virus_aliases(aliases)

        self.assertEqual(viral_prep_aliases.plasmid_name, "AiP123")
        self.assertEqual(viral_prep_aliases.material_id, "AiV456")
        self.assertEqual(viral_prep_aliases.full_genome_name, "UnknownVirus")

    def test_map_full_genome_name(self):
        """Tests that genome name is mapped as expected."""
        response_data = {
            "data": [
                {"aliases": [{"name": "AiP123"}, {"name": "rAAV-MGT_789"}]}
            ]
        }
        response_data2 = {
            "data": [
                {"aliases": [{"name": "rAAV-MGT_789"}, {"name": "AiP123"}]}
            ]
        }
        response_data3 = {
            "data": [{"aliases": [{"name": None}, {"name": "AiP123"}]}]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response_data

        mock_response2 = MagicMock()
        mock_response2.json.return_value = response_data2

        mock_response3 = MagicMock()
        mock_response3.json.return_value = response_data3

        handler = TarsResponseHandler()
        genome_name = handler.map_full_genome_name(
            mock_response, plasmid_name="AiP123"
        )

        genome_name2 = handler.map_full_genome_name(
            mock_response2, plasmid_name="AiP123"
        )

        genome_name3 = handler.map_full_genome_name(
            mock_response3, plasmid_name="AiP123"
        )

        self.assertEqual(genome_name, "rAAV-MGT_789")
        self.assertEqual(genome_name2, "rAAV-MGT_789")
        self.assertIsNone(genome_name3)

    def test_map_lot_to_injection_materials(self):
        """Tests that prep lot is mapped to ViralMaterial as expected."""
        response_data = {
            "lot": "12345",
            "datePrepped": "2023-12-15T12:34:56Z",
            "viralPrep": {
                "viralPrepType": {"name": ViralPrepTypes.CRUDE_SOP.value},
                "virus": {
                    "aliases": [
                        {"name": "AiP123"},
                        {"name": "AiV456"},
                    ]
                },
            },
        }

        handler = TarsResponseHandler()
        viral_prep_aliases = ViralPrepAliases(
            material_id="AiV456",
            full_genome_name="rAAV-MGT_789",
            plasmid_name="AiP123",
        )
        injection_material = handler.map_lot_to_injection_material(
            viral_prep_lot=response_data, viral_prep_aliases=viral_prep_aliases
        )
        expected_tars_virus_ids = TarsVirusIdentifiers(
            virus_tars_id="AiV456",
            plasmid_tars_alias="AiP123",
            prep_lot_number="12345",
            prep_date=date(2023, 12, 15),
            prep_type=VirusPrepType.CRUDE,
            prep_protocol="SOP#VC002",
        )

        expected_injection_material = ViralMaterial(
            name="rAAV-MGT_789", tars_identifiers=expected_tars_virus_ids
        )
        self.assertIsInstance(injection_material, ViralMaterial)
        self.assertEqual(injection_material, expected_injection_material)

    def test_map_lot_to_injection_materials_validation_error(self):
        """Tests that prep lot is mapped to ViralMaterial even if there is a
        validation error."""
        response_data = {
            "lot": "12345",
            "datePrepped": "2023-12-15T12:34:56Z",
            "viralPrep": {
                "viralPrepType": {"name": ViralPrepTypes.CRUDE_SOP.value},
                "virus": {
                    "aliases": [
                        {"name": "AiP123"},
                        {"name": "AiV456"},
                    ]
                },
            },
        }

        handler = TarsResponseHandler()
        viral_prep_aliases = ViralPrepAliases(
            material_id="AiV456", plasmid_name="AiP123", full_genome_name=None
        )
        injection_material = handler.map_lot_to_injection_material(
            viral_prep_lot=response_data, viral_prep_aliases=viral_prep_aliases
        )
        expected_tars_virus_ids = TarsVirusIdentifiers(
            virus_tars_id="AiV456",
            plasmid_tars_alias="AiP123",
            prep_lot_number="12345",
            prep_date=date(2023, 12, 15),
            prep_type=VirusPrepType.CRUDE,
            prep_protocol="SOP#VC002",
        )

        expected_injection_material = ViralMaterial.model_construct(
            name=None, tars_identifiers=expected_tars_virus_ids
        )
        self.assertIsInstance(injection_material, ViralMaterial)
        self.assertEqual(injection_material, expected_injection_material)


if __name__ == "__main__":
    unittest.main()
