"""Tests NSB 2019 data model is parsed correctly"""

import json
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.procedures import BrainInjection

from aind_metadata_service.sharepoint.nsb2019.mapping import MappedNSBList
from aind_metadata_service.sharepoint.nsb2019.models import NSBList

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
DIR_RAW = TEST_DIR / "resources" / "sharepoint" / "nsb2019" / "raw"
DIR_MAP = TEST_DIR / "resources" / "sharepoint" / "nsb2019" / "mapped"
LIST_ITEM_FILE_NAMES = os.listdir(DIR_RAW)
sorted(LIST_ITEM_FILE_NAMES)
LIST_ITEM_FILE_PATHS = [DIR_RAW / str(f) for f in LIST_ITEM_FILE_NAMES]
MAPPED_ITEM_FILE_NAMES = os.listdir(DIR_MAP)
sorted(MAPPED_ITEM_FILE_NAMES)
MAPPED_FILE_PATHS = [DIR_MAP / str(f) for f in MAPPED_ITEM_FILE_NAMES]


class TestNSB2019Parsers(TestCase):
    """Tests methods in NSB2019Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.list_items = cls._load_json_files()

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

    def test_parser(self):
        """Checks that raw data is parsed correctly"""
        for list_item in self.list_items:
            raw_data = list_item[0]
            expected_mapped_data = list(list_item[1])
            expected_mapped_data.sort(key=lambda x: str(x))
            raw_file_name = list_item[2]
            logging.debug(f"Processing file: {raw_file_name}")
            nsb_model = NSBList.parse_obj(raw_data)
            mapped_model = MappedNSBList(nsb=nsb_model)
            mapped_procedures = mapped_model.get_procedures()
            mapped_procedure_json = [
                json.loads(p.json()) for p in mapped_procedures
            ]
            mapped_procedure_json.sort(key=lambda x: str(x))

            self.assertEqual(expected_mapped_data, mapped_procedure_json)

    def test_properties(self):
        """Tests that the properties are parsed correctly."""
        list_item = self.list_items[0]
        raw_data = deepcopy(list_item[0])
        nsb_model = NSBList.parse_obj(raw_data)
        mapped_model = MappedNSBList(nsb=nsb_model)
        props = []
        for k in dir(mapped_model.__class__):
            cls = mapped_model.__class__
            attr = getattr(cls, k)
            if isinstance(attr, property):
                props.append(getattr(mapped_model, k))
        self.assertEqual(117, len(props))

    def test_inj_mapping_edge_cases(self):
        """Tests the case where there is an INJ procedure, but the inj types
        are malformed. It should create generic BrainInjection objects."""

        list_item = self.list_items[0]
        raw_data = deepcopy(list_item[0])
        raw_data["Inj1Type"] = "Select..."
        raw_data["Inj2Type"] = "Nanoject (Pressure)"
        raw_data["Procedure"] = "Stereotaxic Injection"
        raw_data["Virus_x0020_A_x002f_P"] = "3 lambda"
        raw_data["AP2ndInj"] = "2 lambda"
        raw_data["ImplantIDCoverslipType"] = "3.5"
        nsb_model = NSBList.parse_obj(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        mapped_procedure = mapper.get_procedures()
        self.assertTrue(isinstance(mapped_procedure[0], BrainInjection))
        self.assertTrue(isinstance(mapped_procedure[1], BrainInjection))
        raw_data["Inj2Type"] = "Select..."
        nsb_model = NSBList.parse_obj(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        mapped_procedure = mapper.get_procedures()
        self.assertTrue(isinstance(mapped_procedure[0], BrainInjection))
        self.assertTrue(isinstance(mapped_procedure[1], BrainInjection))
        self.assertIsNone(mapper._parse_basic_float_str("one"))


if __name__ == "__main__":
    unittest_main()
