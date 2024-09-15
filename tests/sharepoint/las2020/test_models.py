"""Tests NSP data models are created correctly"""

import json
import logging
import os
from pathlib import Path
from typing import List
from unittest import TestCase
from unittest import main as unittest_main

from aind_metadata_service.sharepoint.las2020.models import LASList, Protocol

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
SHAREPOINT_DIR = TEST_DIR / "resources" / "sharepoint" / "las2020" / "raw"
LIST_ITEM_FILE_NAMES = os.listdir(SHAREPOINT_DIR)
LIST_ITEM_FILE_PATHS = [SHAREPOINT_DIR / str(f) for f in LIST_ITEM_FILE_NAMES]
LIST_ITEM_FILE_PATHS.sort()


class TestLASModels(TestCase):
    """Tests methods in NSPList class"""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.list_items = cls._load_json_files()

    @staticmethod
    def _load_json_files() -> List[dict]:
        """Reads test data into json"""
        list_items = []
        for file_path in LIST_ITEM_FILE_PATHS:
            with open(file_path) as f:
                contents = json.load(f)
            list_items.append(contents)
        return list_items

    def test_models_parsed(self):
        """Tests that the given list item files are parsed without error."""
        for index in range(len(self.list_items)):
            list_item = self.list_items[index]
            logging.debug(f"Processing file: {LIST_ITEM_FILE_NAMES[index]}")
            las_model = LASList.model_validate(list_item)
            self.assertEqual(
                las_model.author_id, int(list_item.get("AuthorId"))
            )

    def test_optional_enum_meta_case(self):
        """Tests optional enum wrapper returns None as expected."""
        list_item = self.list_items[0]
        las_model = LASList.model_validate(list_item)
        self.assertEqual(
            Protocol.N_2212_INVESTIGATING_BRAI, las_model.protocol
        )
        self.assertIsNone(las_model.bc_type)


if __name__ == "__main__":
    unittest_main()
