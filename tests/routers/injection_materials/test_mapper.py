"""Tests mapper module"""

import json
import os
import unittest
from datetime import date
from pathlib import Path

from aind_data_schema.core.procedures import (
    TarsVirusIdentifiers,
    ViralMaterial,
    VirusPrepType,
)

from aind_metadata_service.backends.tars.models import (
    Alias,
    MoleculeResponse,
    PrepLotResponse,
)
from aind_metadata_service.routers.injection_materials.mapper import (
    Mapper,
    PrepProtocols,
    ViralPrepAliases,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
RESOURCE_DIR = TEST_DIR / "resources" / "backends" / "tars"


class TestMapper(unittest.TestCase):
    """Tests methods in Mapper class"""

    @classmethod
    def setUpClass(cls):
        """Sets up class with preloaded info"""
        with open(RESOURCE_DIR / "raw_prep_lot_response.json", "r") as f:
            raw_prep_lot_response_json = json.load(f)

        with open(RESOURCE_DIR / "raw_molecules_response.json", "r") as f:
            raw_molecules_response_json = json.load(f)

        prep_lot_response = PrepLotResponse.model_validate_json(
            json.dumps(raw_prep_lot_response_json)
        )
        molecule_response = MoleculeResponse.model_validate_json(
            json.dumps(raw_molecules_response_json)
        )
        cls.molecule_response = molecule_response
        cls.mapper = Mapper(prep_lot_data=prep_lot_response.data[0])

    def test_map_prep_type(self):
        """Tests viral_prep_types are mapped correctly"""

        self.assertEqual(
            (VirusPrepType.CRUDE, PrepProtocols.SOP_VC002),
            self.mapper._map_prep_type("Crude-SOP#VC002"),
        )
        self.assertEqual(
            (VirusPrepType.PURIFIED, PrepProtocols.SOP_VC003),
            self.mapper._map_prep_type("Purified-SOP#VC003"),
        )
        self.assertEqual(
            (VirusPrepType.CRUDE, PrepProtocols.HGT),
            self.mapper._map_prep_type("Crude-HGT"),
        )
        self.assertEqual(
            (None, PrepProtocols.SOP_VC001),
            self.mapper._map_prep_type("Rabies-SOP#VC001"),
        )
        self.assertEqual(
            (VirusPrepType.CRUDE, PrepProtocols.SOP_VC004),
            self.mapper._map_prep_type("CrudePHPeB-SOP#VC004"),
        )
        self.assertEqual(
            (VirusPrepType.CRUDE, PrepProtocols.MGT2),
            self.mapper._map_prep_type("Crude-MGT#2.0"),
        )
        self.assertEqual(
            (VirusPrepType.CRUDE, PrepProtocols.MGT1),
            self.mapper._map_prep_type("Crude-MGT#1.0"),
        )
        self.assertEqual(
            (VirusPrepType.PURIFIED, PrepProtocols.MGT1),
            self.mapper._map_prep_type("Purified-MGT#1.0"),
        )
        self.assertEqual(
            (None, None), self.mapper._map_prep_type("PHPeB-SOP-UW")
        )
        self.assertEqual(
            (VirusPrepType.CRUDE, PrepProtocols.HGT1),
            self.mapper._map_prep_type("Crude-HGT#1.0"),
        )
        self.assertEqual((None, None), self.mapper._map_prep_type("VTC-AAV1"))
        self.assertEqual((None, None), self.mapper._map_prep_type("Unknown"))
        self.assertEqual(
            (None, None),
            self.mapper._map_prep_type(
                "Iodixanol gradient purification (large scale preps)"
            ),
        )
        self.assertEqual(
            (None, None), self.mapper._map_prep_type("some_other_input")
        )

    def test_map_virus_aliases(self):
        """Tests that aliases are mapped to fields as expected."""
        aliases = [
            Alias(name="AiP123"),
            Alias(name="AiV456"),
            Alias(name="UnknownVirus"),
            Alias(name=None),
        ]

        viral_prep_aliases = self.mapper.map_virus_aliases(aliases)

        self.assertEqual(viral_prep_aliases.plasmid_name, "AiP123")
        self.assertEqual(viral_prep_aliases.material_id, "AiV456")
        self.assertEqual(viral_prep_aliases.full_genome_name, "UnknownVirus")

    def test_map_full_genome_name(self):
        """Tests _map_full_genome_name method."""

        self.assertEqual(
            "UnknownVirus",
            self.mapper.map_full_genome_name(
                plasmid_name="AiP123",
                genome_name="UnknownVirus",
                molecule_aliases=[],
            ),
        )
        self.assertIsNone(
            self.mapper.map_full_genome_name(
                plasmid_name="AiP123", genome_name=None, molecule_aliases=[]
            )
        )
        self.assertEqual(
            "rAAV-MGT_789",
            self.mapper.map_full_genome_name(
                plasmid_name="AiP123",
                genome_name=None,
                molecule_aliases=[
                    Alias(name="rAAV-MGT_789"),
                    Alias(name="AiP123"),
                ],
            ),
        )
        self.assertEqual(
            "rAAV-MGT_789",
            self.mapper.map_full_genome_name(
                plasmid_name="AiP123",
                genome_name=None,
                molecule_aliases=[
                    Alias(name="AiP123"),
                    Alias(name="rAAV-MGT_789"),
                ],
            ),
        )
        self.assertIsNone(
            self.mapper.map_full_genome_name(
                plasmid_name="AiP123",
                genome_name=None,
                molecule_aliases=[
                    Alias(name="AiP123"),
                    Alias(name="AiP123"),
                ],
            ),
        )

    def test_map_to_viral_material_valid(self):
        """Tests map_to_viral_material method when valid model returned"""

        viral_material = self.mapper.map_to_viral_material(
            viral_prep_aliases=ViralPrepAliases(
                material_id="AiV456",
                plasmid_name="AiP123",
                full_genome_name="rAAV-MGT_789",
            )
        )
        expected_output = ViralMaterial(
            name="rAAV-MGT_789",
            tars_identifiers=TarsVirusIdentifiers(
                virus_tars_id="AiV456",
                plasmid_tars_alias="AiP123",
                prep_lot_number="VT3214g",
                prep_date=date(2023, 2, 4),
                prep_type="Purified",
                prep_protocol="SOP#VC003",
            ),
            addgene_id=None,
            titer=None,
            titer_unit="gc/mL",
        )
        self.assertEqual(expected_output, viral_material)

    def test_map_to_viral_material_invalid(self):
        """Tests map_to_viral_material method when invalid model returned"""

        viral_material = self.mapper.map_to_viral_material(
            viral_prep_aliases=ViralPrepAliases(
                material_id="AiV456",
                plasmid_name="AiP123",
                full_genome_name=None,
            )
        )
        expected_output = ViralMaterial.model_construct(
            name=None,
            tars_identifiers={
                "virus_tars_id": "AiV456",
                "plasmid_tars_alias": "AiP123",
                "prep_lot_number": "VT3214g",
                "prep_date": date(2023, 2, 4),
                "prep_type": "Purified",
                "prep_protocol": "SOP#VC003",
            },
            addgene_id=None,
            titer=None,
            titer_unit="gc/mL",
        )
        self.assertEqual(expected_output, viral_material)


if __name__ == "__main__":
    unittest.main()
