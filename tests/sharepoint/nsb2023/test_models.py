import json
import logging
import os
from pathlib import Path
from typing import List
from unittest import TestCase
from unittest import main as unittest_main
from copy import deepcopy

from aind_metadata_service.sharepoint.nsb2023.models import NSBList2023

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
SHAREPOINT_DIR = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "raw"
LIST_ITEM_FILE_NAMES = os.listdir(SHAREPOINT_DIR)
LIST_ITEM_FILE_PATHS = [SHAREPOINT_DIR / str(f) for f in LIST_ITEM_FILE_NAMES]


class TestNSB2023Models(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.list_items = cls._load_json_files()

    @staticmethod
    def _load_json_files() -> List[dict]:
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
            nsb_model = NSBList2023.parse_obj(list_item)
            self.assertEqual(
                nsb_model.author_id, int(list_item.get("AuthorId"))
            )

    def test_aberrant_data_parsed(self):
        """Tests that certain edge cases get handled correctly"""
        list_item = deepcopy(self.list_items[0])
        # Test that numeric entries instead of strings will also get parsed
        list_item["Inj2Angle_v2"] = 20
        list_item["Inj1Current"] = 21
        list_item["Age_x0020_at_x0020_Injection"] = 22
        # Test that malformed or null types get mapped to None
        list_item["Inj1Type"] = "Select..."
        list_item["Inj1IontoTime"] = "5 min 30 sec"
        list_item["Inj2IontoTime"] = 5
        list_item["Inj3IontoTime"] = "5 min"
        # Check that the types are being mapped correctly
        list_item["Sex"] = "Select..."
        list_item["CraniotomyType"] = "Select..."
        nsb_model = NSBList2023.parse_obj(list_item)
        self.assertEqual(20, nsb_model.inj2_angle_v2)
        self.assertEqual(21, nsb_model.inj1_current)
        self.assertEqual(22, nsb_model.age_at_injection)
        self.assertIsNone(nsb_model.inj1_type)
        self.assertEqual(5.5, nsb_model.inj1_ionto_time)
        self.assertEqual(5, nsb_model.inj2_ionto_time)
        self.assertEqual(5, nsb_model.inj3_ionto_time)
        self.assertEqual(None, nsb_model.sex)
        self.assertEqual(None, nsb_model.craniotomy_type)


if __name__ == "__main__":
    unittest_main()
