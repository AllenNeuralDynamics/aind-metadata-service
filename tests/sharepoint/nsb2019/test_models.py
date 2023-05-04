"""Tests NSB 2019 data models are created correctly"""

import json
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase
from unittest import main as unittest_main

from aind_metadata_service.sharepoint.nsb2019.models import NSBList, Sex

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
SHAREPOINT_DIR = TEST_DIR / "resources" / "sharepoint" / "nsb2019" / "raw"
LIST_ITEM_FILE_NAMES = os.listdir(SHAREPOINT_DIR)
LIST_ITEM_FILE_PATHS = [SHAREPOINT_DIR / str(f) for f in LIST_ITEM_FILE_NAMES]


class TestNSB2019Models(TestCase):
    """Tests methods in NSBList2019 class"""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.list_items = cls._load_json_files()

    @staticmethod
    def _load_json_files() -> List[Tuple[dict, str]]:
        """Reads test data into json"""
        list_items = []
        for file_path in LIST_ITEM_FILE_PATHS:
            with open(file_path) as f:
                contents = json.load(f)
            list_items.append((contents, file_path.name))
        list_items.sort(key=lambda x: x[1])
        return list_items

    def test_models_parsed(self):
        """Tests that the given list item files are parsed without error."""
        for index in range(len(self.list_items)):
            list_item = self.list_items[index][0]
            filename = self.list_items[index][1]
            logging.debug(f"Processing file: {filename}")
            nsb_model = NSBList.parse_obj(list_item)
            self.assertEqual(nsb_model.author_id, list_item.get("AuthorId"))

    def test_aberrant_data_parsed(self):
        """Tests that certain edge cases get handled correctly"""
        list_item = deepcopy(self.list_items[0][0])
        # Test that numeric entries instead of strings will also get parsed
        list_item["Age_x0020_at_x0020_Injection"] = "22"
        # Test that malformed or null types get mapped to None
        list_item["Inj1Type"] = "Wrong string"
        list_item["HPDurotomy"] = None
        # Check that the sex types are being mapped correctly
        list_item["Sex"] = "Female"
        nsb_model = NSBList.parse_obj(list_item)
        self.assertEqual("22", nsb_model.age_at_injection)
        self.assertIsNone(nsb_model.inj1_type)
        self.assertIsNone(nsb_model.hp_durotomy)
        self.assertEqual(Sex.FEMALE, nsb_model.sex)


if __name__ == "__main__":
    unittest_main()
