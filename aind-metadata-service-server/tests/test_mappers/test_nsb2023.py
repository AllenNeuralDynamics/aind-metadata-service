"""Tests NSB 2023 data model is parsed correctly"""

import json
import logging
import os
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple, Callable
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.core.procedures import BrainInjection, CraniotomyType, HeadframeMaterial
from aind_sharepoint_service_async_client.models.nsb2023_list import NSB2023List
from aind_metadata_service_server.mappers.nsb2023 import (
        MappedNSBList,
        HeadPostInfo,
        HeadPost,
        HeadPostType,
)

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
DIR_RAW = TEST_DIR / "resources" / "nsb2023" / "raw"
DIR_MAP = TEST_DIR / "resources" / "nsb2023" / "mapped"
INTENDED_RAW = (
    TEST_DIR
    / "resources"
    / "nsb2023"
    / "nsb2023_intended_measurements.json"
)
TEST_EXAMPLES = (
    TEST_DIR
    / "resources"
    / "nsb2023"
    / "nsb2023_string_entries.json"
)
LIST_ITEM_FILE_NAMES = os.listdir(DIR_RAW)
sorted(LIST_ITEM_FILE_NAMES)
LIST_ITEM_FILE_PATHS = [DIR_RAW / str(f) for f in LIST_ITEM_FILE_NAMES]
MAPPED_ITEM_FILE_NAMES = os.listdir(DIR_MAP)
sorted(MAPPED_ITEM_FILE_NAMES)
MAPPED_FILE_PATHS = [DIR_MAP / str(f) for f in MAPPED_ITEM_FILE_NAMES]


class TestNSB2023Parsers(TestCase):
    """Tests methods in NSB2023Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.list_items = cls._load_json_files()
        with open(INTENDED_RAW) as f:
            cls.intended = json.load(f)

    @staticmethod
    def _load_json_files() -> List[Tuple[dict, dict, str]]:
        """Reads raw data and expected data into json"""
        list_items = []
        for file_path in LIST_ITEM_FILE_PATHS:
            mapped_file_path = (
                file_path.parent.parent
                / "mapped"
                / ("mapped_" + file_path.name)
            )
            with open(file_path) as f:
                contents = json.load(f)
            with open(mapped_file_path, encoding="utf-8") as f:
                mapped_contents = json.load(f)
            list_items.append((contents, mapped_contents, file_path.name))
            list_items.sort(key=lambda x: x[2])
        return list_items

    def test_procedures_parser(self):
        """Checks that raw procedures data is parsed correctly"""
        for list_item in self.list_items:
            raw_data = list_item[0]
            expected_mapped_data = list_item[1]
            raw_file_name = list_item[2]
            nsb_model = NSB2023List.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            mapped_procedure = mapper.get_surgeries()  # Updated method name
            mapped_procedure_json = [
                model.model_dump_json() for model in mapped_procedure
            ]
            mapped_procedure_json_parsed = [
                json.loads(json_str) for json_str in mapped_procedure_json
            ]
            if raw_file_name == "list_item5.json":
                with open("actual_mapped_list_item5.json", "w") as f:
                    json.dump(mapped_procedure_json_parsed, f, indent=2)
            self.assertEqual(
                expected_mapped_data, mapped_procedure_json_parsed
            )

    def test_intended_measurements_parser(self):
        """Checks that raw fiber data is parsed correctly."""
        raw_data = self.intended
        expected_mapped_data = [
            {
                "fiber_name": None,
                "intended_measurement_R": "acetylcholine",
                "intended_measurement_G": "calcium",
                "intended_measurement_B": "GABA",
                "intended_measurement_Iso": "control",
            },
            {
                "fiber_name": "Fiber_0",
                "intended_measurement_R": "acetylcholine",
                "intended_measurement_G": "dopamine",
                "intended_measurement_B": "GABA",
                "intended_measurement_Iso": "control",
            },
            {
                "fiber_name": "Fiber_1",
                "intended_measurement_R": "acetylcholine",
                "intended_measurement_G": "dopamine",
                "intended_measurement_B": "glutamate",
                "intended_measurement_Iso": "control",
            },
            {
                "fiber_name": "Fiber_0",
                "intended_measurement_R": "norepinephrine",
                "intended_measurement_G": "calcium",
                "intended_measurement_B": "glutamate",
                "intended_measurement_Iso": "voltage",
            },
        ]
        nsb_model = NSB2023List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        mapped_intended = mapper.get_intended_measurements()
        mapped_intended_json = [
            model.model_dump_json() for model in mapped_intended
        ]
        mapped_intended_json_parsed = [
            json.loads(json_str) for json_str in mapped_intended_json
        ]
        self.assertEqual(expected_mapped_data, mapped_intended_json_parsed)

    def test_properties(self):
        """Tests that the properties are parsed correctly."""
        list_item = self.list_items[0]
        raw_data = deepcopy(list_item[0])
        nsb_model = NSB2023List.model_validate(raw_data)
        mapped_model = MappedNSBList(nsb=nsb_model)
        props = []
        for k in dir(mapped_model.__class__):
            cls = mapped_model.__class__
            attr = getattr(cls, k)
            if isinstance(attr, property):
                props.append(getattr(mapped_model, k))
        self.assertGreater(len(props), 100)

    def test_parse_basic_float_str(self):
        """Tests parsing of basic float strings"""
        self.assertEqual(MappedNSBList._parse_basic_float_str("0.25"), 0.25)
        self.assertIsNone(MappedNSBList._parse_basic_float_str("abc"))

    def test_parse_basic_decimal_str(self):
        """Tests parsing of basic decimal strings"""
        self.assertEqual(
            MappedNSBList._parse_basic_decimal_str("0.25"), Decimal(0.25)
        )
        self.assertIsNone(MappedNSBList._parse_basic_decimal_str("abc"), None)
        
    def test_craniotomy_edge_case(self):
        """Tests other craniotomy cases"""
        # Check WHC type
        list_item = self.list_items[2] if len(self.list_items) > 2 else self.list_items[0]
        raw_data = deepcopy(list_item[0])
        raw_data["Procedure"] = "WHC NP"
        raw_data["CraniotomyType"] = "WHC NP"
        nsb_model1 = NSB2023List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model1)
        mapped_procedure1 = mapper.get_surgeries()
        
        # Find craniotomy procedure
        cran_proc1 = None
        for surgery in mapped_procedure1:
            for proc in surgery.procedures:
                if hasattr(proc, "craniotomy_type"):
                    cran_proc1 = proc
                    break
            if cran_proc1:
                break
                
        if cran_proc1:
            self.assertEqual(
                CraniotomyType.WHC, getattr(cran_proc1, "craniotomy_type")
            )

        # Check OTHER type
        raw_data["Procedure"] = "WHC NP"
        raw_data["CraniotomyType"] = "Select..."
        nsb_model2 = NSB2023List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model2)
        mapped_procedure2 = mapper.get_surgeries()
        
        # Find craniotomy procedure
        cran_proc2 = None
        for surgery in mapped_procedure2:
            for proc in surgery.procedures:
                if hasattr(proc, "craniotomy_type"):
                    cran_proc2 = proc
                    break
            if cran_proc2:
                break
                
        if cran_proc2:
            self.assertIsNone(getattr(cran_proc2, "craniotomy_type"))

    def test_has_cran_procedure(self):
        """Test craniotomy procedure detection"""
        if self.list_items:
            raw_data = deepcopy(self.list_items[0][0])
            raw_data["Procedure"] = "Visual Ctx 2P"  # Known craniotomy procedure
            nsb_model = NSB2023List.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            self.assertTrue(mapper.has_cran_procedure())

    def test_has_hp_procedure(self):
        """Test headpost procedure detection"""
        if self.list_items:
            raw_data = deepcopy(self.list_items[0][0])
            raw_data["Procedure"] = "HP Only"  # Known headpost procedure
            nsb_model = NSB2023List.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            self.assertTrue(mapper.has_hp_procedure())

    def test_injection_edge_case(self):
        """Tests the case where there is an INJ procedure, but the inj types
        are malformed. It should create generic BrainInjection objects."""
        if len(self.list_items) > 3:
            list_item = self.list_items[3]
            raw_data = deepcopy(list_item[0])
            raw_data["Inj1Type"] = "Select..."
            nsb_model = NSB2023List.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            mapped_procedure = mapper.get_surgeries()
            
            # Check if any procedure is a BrainInjection
            proc_types = []
            for surgery in mapped_procedure:
                proc_types.extend([type(p) for p in surgery.procedures])
            
            self.assertTrue(BrainInjection in proc_types)

    def test_single_file_load(self):
        """Test loading a single file to debug issues"""
        if self.list_items:
            raw_data = self.list_items[0][0]
            raw_file_name = self.list_items[0][2]
            print(f"Testing single file: {raw_file_name}")
            
            nsb_model = NSB2023List.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            
            # Test basic properties
            self.assertIsNotNone(mapper.aind_procedure)
            
            # Test surgery generation
            surgeries = mapper.get_surgeries()
            self.assertIsInstance(surgeries, list)
            print(f"Generated {len(surgeries)} surgeries")


    def test_headpost_info_from_hp_and_hp_type(self):
        """Test HeadPostInfo.from_hp_and_hp_type method"""
        # Test Visual Ctx with Mesoscope
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.VISUAL_CTX, 
            hp_type=HeadPostType.MESOSCOPE
        )
        self.assertEqual(hp_info.headframe_type, "Visual Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-10")
        self.assertEqual(hp_info.well_type, "Mesoscope")
        self.assertEqual(hp_info.well_part_number, "0160-200-20")
        self.assertIsNone(hp_info.headframe_material)
        
        # Test WHC NP with WHC NP well
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.WHC_NP, 
            hp_type=HeadPostType.WHC_NP
        )
        self.assertEqual(hp_info.headframe_type, "WHC NP")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-42")
        self.assertEqual(hp_info.well_type, "WHC NP")
        self.assertEqual(hp_info.well_part_number, "0160-055-08")
        self.assertIsNone(hp_info.headframe_material)
        
        # Test WHC 2P with WHC 2P well
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.WHC_2P, 
            hp_type=HeadPostType.WHC_2P
        )
        self.assertEqual(hp_info.headframe_type, "WHC 2P")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-45")
        self.assertEqual(hp_info.well_type, "WHC 2P")
        self.assertEqual(hp_info.well_part_number, "0160-200-62")
        self.assertIsNone(hp_info.headframe_material)
        
        # Test Frontal Ctx with Neuropixel
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.FRONTAL_CTX, 
            hp_type=HeadPostType.NEUROPIXEL
        )
        self.assertEqual(hp_info.headframe_type, "Frontal Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-46")
        self.assertEqual(hp_info.well_type, "Neuropixel")
        self.assertEqual(hp_info.well_part_number, "0160-200-36")
        self.assertIsNone(hp_info.headframe_material)
        
        # Test Motor Ctx with CAM well
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.MOTOR_CTX, 
            hp_type=HeadPostType.CAM
        )
        self.assertEqual(hp_info.headframe_type, "Motor Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-51")
        self.assertEqual(hp_info.well_type, "Scientifica (CAM)")
        self.assertEqual(hp_info.well_part_number, "Rev A")
        self.assertIsNone(hp_info.headframe_material)
        
        # Test DHC with DHC well (should have titanium material)
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.DHC, 
            hp_type=HeadPostType.DHC_WELL
        )
        self.assertEqual(hp_info.headframe_type, "DHC")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-57")
        self.assertEqual(hp_info.well_type, "DHC well")
        self.assertEqual(hp_info.well_part_number, "0160-075-01")
        self.assertEqual(hp_info.headframe_material, HeadframeMaterial.TITANIUM)
        
        # Test with None values
        hp_info = HeadPostInfo.from_hp_and_hp_type(hp=None, hp_type=None)
        self.assertIsNone(hp_info.headframe_type)
        self.assertIsNone(hp_info.headframe_part_number)
        self.assertIsNone(hp_info.well_type)
        self.assertIsNone(hp_info.well_part_number)
        self.assertIsNone(hp_info.headframe_material)
        
        # Test with unsupported headpost type (should return None for part number)
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.AI_HEADBAR, 
            hp_type=HeadPostType.NO_WELL
        )
        self.assertEqual(hp_info.headframe_type, "AI Straight bar")
        self.assertIsNone(hp_info.headframe_part_number)
        self.assertEqual(hp_info.well_type, "No Well")
        self.assertIsNone(hp_info.well_part_number)  
        self.assertIsNone(hp_info.headframe_material)
        
        # Test mixed known/unknown combinations
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.VISUAL_CTX, 
            hp_type=HeadPostType.NO_WELL
        )
        self.assertEqual(hp_info.headframe_type, "Visual Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-10")
        self.assertEqual(hp_info.well_type, "No Well")
        self.assertIsNone(hp_info.well_part_number) 
        self.assertIsNone(hp_info.headframe_material)

    def test_burr_hole_info_edge_case(self):
        """Test burr_hole_info returns empty info when no burr hole exists"""
        nsb_model = NSB2023List.model_construct()
        mapper = MappedNSBList(nsb=nsb_model)
        bh_info = mapper.burr_hole_info(0)
        self.assertIsNone(bh_info.hemisphere)

    def test_other_headframe_edge_case(self):
        """Tests case when headframe has no during info"""
        nsb_model = NSB2023List.model_construct(Procedure="HP Only")
        mapper = MappedNSBList(nsb=nsb_model)
        procedures = mapper.get_surgeries()
        self.assertEqual(len(procedures), 1)

class TestNSB2023StringParsers(TestCase):
    """Tests text field parsers in NSB2023Mapping class. Certain fields, such
    as AP2ndInj, allow the users to input text freely. This has led to entries
    like '+0.8 ANT', '+1.8', ;-3.8mm', etc."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.string_entries = cls._load_json_file()
        cls.blank_model = MappedNSBList(nsb=NSB2023List.model_construct())

    @staticmethod
    def _load_json_file() -> dict:
        """Reads raw data and expected data into json"""
        with open(TEST_EXAMPLES) as f:
            contents = json.load(f)
        return contents

    def _test_parser(self, keys: List[str], parser: Callable) -> None:
        """
        Helper function to test a parser againsts a list of keys in resource
        json file.
        Parameters
        ----------
        keys : List[str]
          Keys of the json fields we want to check
        parser : Callable
          The parser method we want to test

        Returns
        -------
        None
          Will raise an assertion error if the parsers return unexpected values

        """
        for k in keys:
            expected_entries = self.string_entries[k]["unique_entries"]
            for example_key, example_val in expected_entries.items():
                expected = example_val
                actual = parser(example_key)
                self.assertEqual(expected, actual)
        self.assertIsNone(parser(None))

    def test_current_parser(self):
        """Checks that current fields are parsed correctly"""

        c_keys = ["Inj1Current", "Inj2Current", "Inj3Current", "Inj4Current"]
        self._test_parser(c_keys, self.blank_model._parse_current_str)

    def test_length_of_time_parser(self):
        """Checks that length-of-time fields are parsed correctly"""

        lt_keys = [
            "Inj1IontoTime",
            "Inj2IontoTime",
            "Inj3IontoTime",
            "Inj4IontoTime",
        ]
        self._test_parser(lt_keys, self.blank_model._parse_length_of_time_str)

    def test_age_at_injection_parser(self):
        """Checks that age at injection fields are parsed correctly"""
        age_keys = ["Age_x0020_at_x0020_Injection"]
        self._test_parser(age_keys, self.blank_model._parse_basic_float_str)

if __name__ == "__main__":
    unittest_main()