"""Tests NSB 2023 data models are created correctly"""

import json
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import List
from unittest import TestCase
from unittest import main as unittest_main

from aind_metadata_service.sharepoint.nsb2023.models import (
    BurrHoleProcedure,
    During,
    HeadPostInfo2023,
    InjectionType,
    NSBList2023,
)

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
SHAREPOINT_DIR = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "raw"
LIST_ITEM_FILE_NAMES = os.listdir(SHAREPOINT_DIR)
LIST_ITEM_FILE_PATHS = [SHAREPOINT_DIR / str(f) for f in LIST_ITEM_FILE_NAMES]
LIST_ITEM_FILE_PATHS.sort()


class TestNSB2023Models(TestCase):
    """Tests methods in NSBList2023 class"""

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
            nsb_model = NSBList2023.parse_obj(list_item)
            headpost_info = HeadPostInfo2023.from_hp_and_hp_type(
                nsb_model.headpost, nsb_model.headpost_type
            )
            self.assertEqual(
                nsb_model.author_id, int(list_item.get("AuthorId"))
            )
            self.assertTrue(
                nsb_model.headpost is None
                or headpost_info.headframe_type is not None
            )

    def test_aberrant_data_parsed(self):
        """Tests that certain edge cases get handled correctly"""
        list_item = deepcopy(self.list_items[0])
        # Test that numeric entries instead of strings will also get parsed
        list_item["Age_x0020_at_x0020_Injection"] = 22
        # Test that malformed or null types get mapped to None
        list_item["Inj1Type"] = "Select..."
        # Check that the types are being mapped correctly
        list_item["Sex"] = "Select..."
        list_item["CraniotomyType"] = "Select..."
        list_item["HeadpostType"] = "Select..."
        list_item["Headpost"] = "Select..."
        nsb_model = NSBList2023.parse_obj(list_item)
        self.assertEqual(22, nsb_model.age_at_injection)
        self.assertIsNone(nsb_model.inj1_type)
        self.assertIsNone(nsb_model.sex)
        self.assertIsNone(nsb_model.craniotomy_type)
        self.assertIsNone(nsb_model.headpost)
        self.assertIsNone(nsb_model.headpost_type)

    def test_booleans(self):
        """Tests boolean methods"""
        list_item = deepcopy(self.list_items[0])
        nsb_model = NSBList2023.parse_obj(list_item)
        self.assertFalse(nsb_model.has_hp_procedure())
        self.assertTrue(nsb_model.has_cran_procedure())
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(1, BurrHoleProcedure.INJECTION)
        )
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(
                1, BurrHoleProcedure.FIBER_IMPLANT
            )
        )
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(2, BurrHoleProcedure.INJECTION)
        )
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(
                2, BurrHoleProcedure.FIBER_IMPLANT
            )
        )
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(3, BurrHoleProcedure.INJECTION)
        )
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(
                3, BurrHoleProcedure.FIBER_IMPLANT
            )
        )
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(4, BurrHoleProcedure.INJECTION)
        )
        self.assertFalse(
            nsb_model.has_burr_hole_procedure(
                4, BurrHoleProcedure.FIBER_IMPLANT
            )
        )

        # Test non-hp procedure
        nsb_model.procedure = "Visual Ctx"
        self.assertFalse(nsb_model.has_hp_procedure())
        self.assertTrue(nsb_model.has_cran_procedure())

        # Test non-hp procedure
        nsb_model.procedure = "Headpost"
        self.assertTrue(nsb_model.has_hp_procedure())
        self.assertFalse(nsb_model.has_cran_procedure())

        # Test None
        nsb_model.procedure = None
        self.assertFalse(nsb_model.has_hp_procedure())
        self.assertFalse(nsb_model.has_cran_procedure())

    def test_parse_info(self):
        """Tests data containers created correctly"""
        list_item = deepcopy(self.list_items[0])
        nsb_model = NSBList2023.parse_obj(list_item)
        burr_hole0_info = nsb_model.burr_hole_info(0)
        burr_hole1_info = nsb_model.burr_hole_info(1)
        burr_hole2_info = nsb_model.burr_hole_info(2)
        burr_hole3_info = nsb_model.burr_hole_info(3)
        burr_hole4_info = nsb_model.burr_hole_info(4)
        surgery_during_info_x = nsb_model.surgery_during_info(None)
        surgery_during_info_a = nsb_model.surgery_during_info(
            During.INITIAL_SURGERY
        )
        surgery_during_info_b = nsb_model.surgery_during_info(
            During.FOLLOW_UP_SURGERY
        )
        surgery_during_info_c = nsb_model.surgery_during_info(
            During.INITIAL_SURGERY, inj_type=InjectionType.NANOJECT
        )
        surgery_during_info_d = nsb_model.surgery_during_info(
            During.FOLLOW_UP_SURGERY, inj_type=InjectionType.IONTOPHORESIS
        )
        surgery_during_info_e = nsb_model.surgery_during_info(
            During.INITIAL_SURGERY, inj_type=InjectionType.IONTOPHORESIS
        )
        surgery_during_info_f = nsb_model.surgery_during_info(
            During.FOLLOW_UP_SURGERY, inj_type=InjectionType.NANOJECT
        )
        self.assertIsNone(burr_hole0_info.during)
        self.assertEqual(None, burr_hole1_info.during)
        self.assertIsNone(burr_hole2_info.during)
        self.assertIsNone(burr_hole3_info.during)
        self.assertIsNone(burr_hole4_info.during)

        self.assertIsNone(surgery_during_info_x.start_date)
        self.assertEqual(25.2, surgery_during_info_a.weight_prior)
        self.assertIsNone(surgery_during_info_b.weight_prior)
        self.assertEqual(25.2, surgery_during_info_c.weight_prior)
        self.assertIsNone(surgery_during_info_d.weight_prior)
        self.assertEqual(25.2, surgery_during_info_e.weight_prior)
        self.assertIsNone(surgery_during_info_f.weight_prior)


if __name__ == "__main__":
    unittest_main()
