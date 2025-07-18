"""Tests methods in mapping module"""

import json
import os
import unittest
from datetime import date
from pathlib import Path

from aind_data_schema.core.procedures import (
    TarsVirusIdentifiers,
    VirusPrepType,
)
from aind_data_schema_models.pid_names import BaseName, PIDName
from aind_tars_service_async_client import Titers
from aind_tars_service_async_client.models import PrepLotData, VirusData

from aind_metadata_service_server.mappers.injection_materials import (
    PrepProtocols,
    TarsMapper,
    TarsVirusInformation,
)
from aind_metadata_service_server.models import ViralMaterialInformation

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources"
)


class TestTarsMapping(unittest.TestCase):
    """Class to test methods for TarsMapper"""

    @classmethod
    def setUp(cls):
        """Set up base test data with prep lot data"""
        with open(RESOURCES_DIR / "prep_lot_example.json", "r") as f:
            prep_lot_example_json = json.load(f)

        with open(RESOURCES_DIR / "virus_data_example.json", "r") as f:
            virus_data_example_json = json.load(f)

        prep_lot_data = PrepLotData.model_validate(prep_lot_example_json)
        virus_data = [
            VirusData.model_validate(m) for m in virus_data_example_json
        ]
        cls.mapper = TarsMapper(
            prep_lot_data=prep_lot_data, virus_data=virus_data
        )

    def test_virus_id(self):
        """Tests virus_id property"""
        self.assertEqual("VIR300001_PHPeB", self.mapper.virus_id)

    def test_map_to_prep_type(self):
        """Tests map_to_prep_type"""
        prep_type_crude = self.mapper._map_to_prep_type("Crude-SOP#VC002")
        prep_type_pure = self.mapper._map_to_prep_type("Purified-SOP#VC003")
        prep_type_none = self.mapper._map_to_prep_type("Unknown")
        prep_type_none2 = self.mapper._map_to_prep_type(None)
        self.assertEqual(VirusPrepType.CRUDE, prep_type_crude)
        self.assertEqual(VirusPrepType.PURIFIED, prep_type_pure)
        self.assertIsNone(prep_type_none)
        self.assertIsNone(prep_type_none2)

    def test_map_to_protocol(self):
        """Tests _map_to_protocol"""

        prep_protocol_mg1 = self.mapper._map_to_protocol("Purified-MGT#1.0")
        prep_protocol_mg2 = self.mapper._map_to_protocol("Crude-MGT#2.0")
        prep_protocol_sop2 = self.mapper._map_to_protocol("Crude-SOP#VC002")
        prep_protocol_sop3 = self.mapper._map_to_protocol("Purified-SOP#VC003")
        prep_protocol_hgt = self.mapper._map_to_protocol("Crude-HGT")
        prep_protocol_sop1 = self.mapper._map_to_protocol("Rabies-SOP#VC001")
        prep_protocol_sop4 = self.mapper._map_to_protocol(
            "CrudePHPeB-SOP#VC004"
        )
        prep_protocol_hgt1 = self.mapper._map_to_protocol("Crude-HGT#1.0")
        prep_protocol_none = self.mapper._map_to_protocol("Unknown")
        prep_protocol_none1 = self.mapper._map_to_protocol(None)
        self.assertEqual(PrepProtocols.MGT1, prep_protocol_mg1)
        self.assertEqual(PrepProtocols.MGT2, prep_protocol_mg2)
        self.assertEqual(PrepProtocols.SOP_VC001, prep_protocol_sop1)
        self.assertEqual(PrepProtocols.SOP_VC002, prep_protocol_sop2)
        self.assertEqual(PrepProtocols.SOP_VC003, prep_protocol_sop3)
        self.assertEqual(PrepProtocols.HGT, prep_protocol_hgt)
        self.assertEqual(PrepProtocols.SOP_VC004, prep_protocol_sop4)
        self.assertEqual(PrepProtocols.HGT1, prep_protocol_hgt1)
        self.assertIsNone(prep_protocol_none)
        self.assertIsNone(prep_protocol_none1)

    def test_map_plasmid_name(self):
        """Tests _map_plasmid_name"""
        aliases = [
            {"name": "alias1", "isPreferred": False},
            {"name": "alias2", "isPreferred": True},
        ]
        self.assertEqual(
            "alias2", self.mapper._map_plasmid_name(aliases=aliases)
        )
        self.assertIsNone(self.mapper._map_plasmid_name(aliases=[]))

    def test_map_stock_titer(self):
        """Tests _map_stock_titer"""
        titers = [Titers(result=123), Titers(result=345)]
        self.assertEqual(123, self.mapper._map_stock_titer(titers=titers))
        self.assertIsNone(self.mapper._map_stock_titer([]))
        self.assertIsNone(self.mapper._map_stock_titer(None))

    def test_map_virus_information(self):
        """Tests _map_virus_information"""
        tars_ids = self.mapper._map_virus_information()
        expected_tars_ids = TarsVirusInformation(
            name="pAAV-7x-TRE-tDTomato",
            plasmid_alias="ExP300001",
            addgene_id="191207",
            rrid="Addgene_191207",
        )
        self.assertEqual(expected_tars_ids, tars_ids)

    def test_map_virus_information_empty(self):
        """Tests _map_virus_information with empty virus list"""
        mapper = TarsMapper(
            prep_lot_data=self.mapper.prep_lot_data, virus_data=[]
        )
        self.assertEqual(
            TarsVirusInformation(), mapper._map_virus_information()
        )

    def test_map_virus_information_first_rrid_edge_case(self):
        """Tests _map_virus_information with first_rrid edge case"""
        mapper = TarsMapper(
            prep_lot_data=self.mapper.prep_lot_data,
            virus_data=[VirusData(rr_id="abc")],
        )
        self.assertEqual(
            TarsVirusInformation(rrid="abc"), mapper._map_virus_information()
        )

    def test_create_addgene_pid_name(self):
        """Tests _create_addgene_pid_name"""

        tars_virus_info_1 = TarsVirusInformation(
            name="pAAV-7x-TRE-tDTomato",
            plasmid_alias="ExP300001",
            addgene_id="191207",
            rrid="Addgene_191207",
        )
        expected_pid_name = PIDName(
            name="pAAV-7x-TRE-tDTomato",
            registry=BaseName(name="Addgene_191207"),
            registry_identifier="191207",
        )
        self.assertEqual(
            expected_pid_name,
            self.mapper._create_addgene_pid_name(tars_virus_info_1),
        )
        self.assertIsNone(
            self.mapper._create_addgene_pid_name(TarsVirusInformation())
        )

    def test_map_to_viral_material_information_valid(self):
        """Tests map_to_viral_material_information valid"""
        viral_info = self.mapper.map_to_viral_material_information()
        expected_viral_info = ViralMaterialInformation(
            material_type="Virus",
            name="pAAV-7x-TRE-tDTomato",
            tars_identifiers=TarsVirusIdentifiers(
                virus_tars_id="VIR300001_PHPeB",
                plasmid_tars_alias="ExP300001",
                prep_lot_number="VT3216G",
                prep_date=date(2022, 2, 4),
                prep_type="Purified",
                prep_protocol="SOP#VC003",
            ),
            addgene_id=PIDName(
                name="pAAV-7x-TRE-tDTomato",
                abbreviation=None,
                registry=BaseName(name="Addgene_191207", abbreviation=None),
                registry_identifier="191207",
            ),
            titer=None,
            titer_unit="gc/mL",
            stock_titer=15000000000000,
        )
        self.assertEqual(expected_viral_info, viral_info)

    def test_map_to_viral_material_information_invalid(self):
        """Tests map_to_viral_material_information invalid"""
        mapper = TarsMapper(prep_lot_data=PrepLotData(lot="abc"))
        viral_info = mapper.map_to_viral_material_information()
        expected_viral_info = ViralMaterialInformation.model_construct(
            material_type="Virus",
            name=None,
            tars_identifiers=TarsVirusIdentifiers(prep_lot_number="abc"),
            addgene_id=None,
            titer=None,
            titer_unit="gc/mL",
            stock_titer=None,
        )
        self.assertEqual(expected_viral_info, viral_info)


if __name__ == "__main__":
    unittest.main()
