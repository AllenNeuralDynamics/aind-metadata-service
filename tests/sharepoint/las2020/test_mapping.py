"""Tests LAS data model is parsed correctly"""

import json
import logging
import os
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase
from unittest import main as unittest_main

from aind_metadata_service.sharepoint.las2020.mapping import MappedLASList
from aind_metadata_service.sharepoint.las2020.models import LASList

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))


TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
DIR_RAW = TEST_DIR / "resources" / "sharepoint" / "las2020" / "raw"
DIR_MAP = TEST_DIR / "resources" / "sharepoint" / "las2020" / "mapped"
LIST_ITEM_FILE_NAMES = os.listdir(DIR_RAW)
sorted(LIST_ITEM_FILE_NAMES)
LIST_ITEM_FILE_PATHS = [DIR_RAW / str(f) for f in LIST_ITEM_FILE_NAMES]
MAPPED_ITEM_FILE_NAMES = os.listdir(DIR_MAP)
sorted(MAPPED_ITEM_FILE_NAMES)
MAPPED_FILE_PATHS = [DIR_MAP / str(f) for f in MAPPED_ITEM_FILE_NAMES]


class TestLASParsers(TestCase):
    """Tests methods in NSPMapping class"""

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
            expected_mapped_data = list_item[1]
            raw_file_name = list_item[1]
            logging.debug(f"Processing file: {raw_file_name}")
            las_model = LASList.model_validate(raw_data)
            mapper = MappedLASList(las=las_model)
            mapped_procedure = mapper.get_procedure(subject_id="000000")
            mapped_procedure_json = mapped_procedure.model_dump_json()
            mapped_procedure_json_parsed = json.loads(mapped_procedure_json)
            self.assertEqual(
                expected_mapped_data, mapped_procedure_json_parsed
            )

    def test_properties(self):
        """Tests that the properties are parsed correctly."""
        list_item = self.list_items[0]
        raw_data = deepcopy(list_item[0])
        las_model = LASList.model_validate(raw_data)
        mapped_model = MappedLASList(las=las_model)
        props = []
        for k in dir(mapped_model.__class__):
            cls = mapped_model.__class__
            attr = getattr(cls, k)
            if isinstance(attr, property):
                props.append(getattr(mapped_model, k))
        self.assertEqual(233, len(props))

    def test_parse_basic_decimal_str(self):
        """Tests parsing of basic decimal strings"""
        self.assertEqual(
            MappedLASList._parse_basic_decimal_str("0.25"), Decimal(0.25)
        )
        self.assertIsNone(MappedLASList._parse_basic_decimal_str("abc"), None)


if __name__ == "__main__":
    unittest_main()
