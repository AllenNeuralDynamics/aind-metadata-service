"""Module for mapping"""
import unittest
from unittest.mock import MagicMock
from datetime import datetime, date
from aind_metadata_service.tars.mapping import (
    TarsResponseHandler,
    ViralPrepTypes,
    VirusPrepType,
    PrepProtocols,
    InjectionMaterial,
)


class TestTarsResponseHandler(unittest.TestCase):
    def test_map_prep_type_and_protocol(self):
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

    def test_convert_datetime(self):
        valid_date = "2023-12-15T12:34:56Z"
        invalid_date = "12/15/2023"

        converted_date = TarsResponseHandler._convert_datetime(valid_date)
        self.assertIsInstance(converted_date, datetime)

        converted_invalid_date = TarsResponseHandler._convert_datetime(
            invalid_date
        )
        self.assertIsNone(converted_invalid_date)

    def test_map_virus_aliases(self):
        aliases = [
            {"name": "AiP123"},
            {"name": "AiV456"},
            {"name": "UnknownVirus"},
        ]

        (
            material_id,
            viral_prep_id,
            full_genome_name,
        ) = TarsResponseHandler._map_virus_aliases(aliases)

        self.assertEqual(material_id, "AiP123")
        self.assertEqual(viral_prep_id, "AiV456")
        self.assertEqual(full_genome_name, "UnknownVirus")

    def test_map_response_to_injection_materials(self):
        response_data = {
            "data": [
                {
                    "lot": "12345",
                    "datePrepped": "2023-12-15T12:34:56Z",
                    "viralPrep": {
                        "viralPrepType": {
                            "name": ViralPrepTypes.CRUDE_SOP.value
                        },
                        "virus": {
                            "aliases": [
                                {"name": "AiP123"},
                                {"name": "AiV456"},
                                {"name": "rAAV-MGT_789"},
                            ]
                        },
                    },
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response_data

        handler = TarsResponseHandler()
        injection_material = handler.map_response_to_injection_materials(
            mock_response
        )
        expected_injection_material = InjectionMaterial(
            name="rAAV-MGT_789",
            material_id="AiP123",
            full_genome_name=None,
            prep_lot_number="12345",
            prep_date=date(2023, 12, 15),
            prep_type=VirusPrepType.CRUDE,
            prep_protocol="SOP#VC002",
        )
        self.assertIsInstance(injection_material, InjectionMaterial)
        self.assertEqual(injection_material, expected_injection_material)


if __name__ == "__main__":
    unittest.main()
