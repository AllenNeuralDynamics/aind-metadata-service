"""Tests NSB 2023 data model is parsed correctly"""

import json
import logging
import os
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.core.procedures import BrainInjection, CraniotomyType

from aind_metadata_service.sharepoint.nsb2023.mapping import (
    BurrHoleInfo,
    HeadPost,
    HeadPostInfo,
    HeadPostType,
    MappedNSBList,
)
from aind_metadata_service.sharepoint.nsb2023.models import NSBList

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
DIR_RAW = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "raw"
DIR_MAP = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "mapped"
INTENDED_RAW = (
    TEST_DIR
    / "resources"
    / "sharepoint"
    / "nsb2023"
    / "nsb2023_intended_measurements.json"
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
            logging.debug(f"Processing file: {raw_file_name}")
            nsb_model = NSBList.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            mapped_procedure = mapper.get_procedure()
            mapped_procedure_json = [
                model.model_dump_json() for model in mapped_procedure
            ]
            mapped_procedure_json_parsed = [
                json.loads(json_str) for json_str in mapped_procedure_json
            ]
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
        nsb_model = NSBList.model_validate(raw_data)
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
        nsb_model = NSBList.model_validate(raw_data)
        mapped_model = MappedNSBList(nsb=nsb_model)
        props = []
        for k in dir(mapped_model.__class__):
            cls = mapped_model.__class__
            attr = getattr(cls, k)
            if isinstance(attr, property):
                props.append(getattr(mapped_model, k))
        self.assertEqual(313, len(props))

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
        list_item = self.list_items[2]
        raw_data = deepcopy(list_item[0])
        raw_data["Procedure"] = "WHC NP"
        raw_data["CraniotomyType"] = "WHC NP"
        nsb_model1 = NSBList.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model1)
        mapped_procedure1 = mapper.get_procedure()
        cran_proc1 = mapped_procedure1[0].procedures[0]
        self.assertEqual(
            CraniotomyType.WHC, getattr(cran_proc1, "craniotomy_type")
        )

        # Check OTHER type
        raw_data["Procedure"] = "WHC NP"
        raw_data["CraniotomyType"] = "Select..."
        nsb_model2 = NSBList.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model2)
        mapped_procedure2 = mapper.get_procedure()
        cran_proc2 = mapped_procedure2[0].procedures[0]
        self.assertIsNone(getattr(cran_proc2, "craniotomy_type"))

    def test_headpost_edge_case(self):
        """Test edge case for HeadPostInfo class constructor"""
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            hp=HeadPost.VISUAL_CTX, hp_type=HeadPostType.MESOSCOPE
        )
        exp_hp_info = HeadPostInfo(
            headframe_type=HeadPost.VISUAL_CTX.value,
            headframe_part_number="0160-100-10",
            well_type=HeadPostType.MESOSCOPE.value,
            well_part_number="0160-200-20",
        )
        self.assertEqual(exp_hp_info, hp_info)

    def test_injection_edge_case(self):
        """Tests the case where there is an INJ procedure, but the inj types
        are malformed. It should create generic BrainInjection objects."""
        list_item = self.list_items[3]
        raw_data = deepcopy(list_item[0])
        raw_data["Inj1Type"] = "Select..."
        nsb_model = NSBList.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        mapped_procedure = mapper.get_procedure()
        proc_types = [type(p) for p in mapped_procedure[0].procedures]
        self.assertTrue(BrainInjection in proc_types)

    def test_burr_hole_to_probe_edge_case(self):
        """Tests edge case where burr hole number greater than 6"""
        list_item = self.list_items[2]
        raw_data = deepcopy(list_item[0])
        nsb_model = NSBList.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        self.assertEqual(BurrHoleInfo(), mapper.burr_hole_info(7))


if __name__ == "__main__":
    unittest_main()
