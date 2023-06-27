"""Tests NSB 2019 string parsers work against examples"""

import json
import os
from pathlib import Path
from unittest import TestCase
from unittest import main as unittest_main

from aind_metadata_service.sharepoint.nsb2019.mapping import MappedNSBList
from aind_metadata_service.sharepoint.nsb2019.models import NSBList

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
TEST_EXAMPLES = (
    TEST_DIR
    / "resources"
    / "sharepoint"
    / "nsb2019"
    / "nsb2019_string_entries.json"
)


class TestNSB2019StringParsers(TestCase):
    """Tests text field parsers in NSB2019Mapping class. Certain fields, such
    as AP2ndInj, allow the users to input text freely. This has led to entries
    like '+0.8 ANT', '+1.8', ;-3.8mm', etc."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.string_entries = cls._load_json_file()
        cls.blank_model = MappedNSBList(nsb=NSBList.construct())

    @staticmethod
    def _load_json_file() -> dict:
        """Reads raw data and expected data into json"""
        with open(TEST_EXAMPLES) as f:
            contents = json.load(f)
        return contents

    def test_ap_parser(self):
        """Checks that ap fields are parsed correctly"""
        expected_ap_2nd_inj = self.string_entries["AP2ndInj"]["unique_entries"]
        expected_hp_ap = self.string_entries["HP_x0020_A_x002f_P"][
            "unique_entries"
        ]
        expected_virus_ap = self.string_entries["Virus_x0020_A_x002f_P"][
            "unique_entries"
        ]
        for example_key, example_val in expected_ap_2nd_inj.items():
            expected = example_val
            actual = self.blank_model._parse_ap_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_hp_ap.items():
            expected = example_val
            actual = self.blank_model._parse_ap_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_virus_ap.items():
            expected = example_val
            actual = self.blank_model._parse_ap_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_ap_str(None))

    def test_dv_parser(self):
        """Checks that dv fields are parsed correctly"""
        expected_dv_2nd_inj = self.string_entries["DV2ndInj"]["unique_entries"]
        expected_dv_fb1 = self.string_entries["FiberImplant1DV"][
            "unique_entries"
        ]
        expected_dv_fb2 = self.string_entries["FiberImplant2DV"][
            "unique_entries"
        ]
        expected_virus_dv = self.string_entries["Virus_x0020_D_x002f_V"][
            "unique_entries"
        ]
        for example_key, example_val in expected_dv_2nd_inj.items():
            expected = example_val
            actual = self.blank_model._parse_dv_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_dv_fb1.items():
            expected = example_val
            actual = self.blank_model._parse_dv_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_dv_fb2.items():
            expected = example_val
            actual = self.blank_model._parse_dv_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_virus_dv.items():
            expected = example_val
            actual = self.blank_model._parse_dv_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_dv_str(None))

    def test_iso_dur_parser(self):
        """Checks that the iso duration fields are parsed correctly"""
        expected_1st_inj_iso_dur = self.string_entries[
            "FirstInjectionIsoDuration"
        ]["unique_entries"]
        expected_2nd_inj_iso_dur = self.string_entries[
            "SecondInjectionIsoDuration"
        ]["unique_entries"]

        for example_key, example_val in expected_1st_inj_iso_dur.items():
            expected = example_val
            actual = self.blank_model._parse_iso_dur_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_2nd_inj_iso_dur.items():
            expected = example_val
            actual = self.blank_model._parse_iso_dur_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_iso_dur_str(None))

    def test_weight_parser(self):
        """Checks that weight fields are parsed correctly"""
        expected_1st_inj_w_a = self.string_entries[
            "FirstInjectionWeightAfter"
        ]["unique_entries"]
        expected_1st_inj_w_b = self.string_entries[
            "FirstInjectionWeightBefor"
        ]["unique_entries"]
        expected_touch_up_w = self.string_entries[
            "Touch_x0020_Up_x0020_Weight_x002"
        ]["unique_entries"]
        expected_w_after = self.string_entries[
            "Weight_x0020_after_x0020_Surgery"
        ]["unique_entries"]
        expected_w_before = self.string_entries[
            "Weight_x0020_before_x0020_Surger"
        ]["unique_entries"]
        expected_2nd_inj_w_a = self.string_entries[
            "SecondInjectionWeightAfter"
        ]["unique_entries"]
        expected_2nd_inj_w_b = self.string_entries[
            "SecondInjectionWeightBefore"
        ]["unique_entries"]

        for example_key, example_val in expected_1st_inj_w_a.items():
            expected = example_val
            actual = self.blank_model._parse_weight_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_1st_inj_w_b.items():
            expected = example_val
            actual = self.blank_model._parse_weight_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_touch_up_w.items():
            expected = example_val
            actual = self.blank_model._parse_weight_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_w_after.items():
            expected = example_val
            actual = self.blank_model._parse_weight_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_w_before.items():
            expected = example_val
            actual = self.blank_model._parse_weight_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_2nd_inj_w_a.items():
            expected = example_val
            actual = self.blank_model._parse_weight_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_2nd_inj_w_b.items():
            expected = example_val
            actual = self.blank_model._parse_weight_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_weight_str(None))

    def test_ml_parser(self):
        """Checks that ml fields are parsed correctly"""
        expected_ml_2nd_inj = self.string_entries["ML2ndInj"]["unique_entries"]
        expected_hp_ml = self.string_entries["HP_x0020_M_x002f_L"][
            "unique_entries"
        ]
        expected_virus_ml = self.string_entries["Virus_x0020_M_x002f_L"][
            "unique_entries"
        ]
        for example_key, example_val in expected_ml_2nd_inj.items():
            expected = example_val
            actual = self.blank_model._parse_ml_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_hp_ml.items():
            expected = example_val
            actual = self.blank_model._parse_ml_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_virus_ml.items():
            expected = example_val
            actual = self.blank_model._parse_ml_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_ml_str(None))

    def test_alt_time_parser(self):
        """Checks that alternating time fields are parsed correctly"""
        expected_inj_1_alt_time = self.string_entries["Inj1AlternatingTime"][
            "unique_entries"
        ]
        expected_inj_2_alt_time = self.string_entries["Inj2AlternatingTime"][
            "unique_entries"
        ]
        for example_key, example_val in expected_inj_1_alt_time.items():
            expected = example_val
            actual = self.blank_model._parse_alt_time_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_inj_2_alt_time.items():
            expected = example_val
            actual = self.blank_model._parse_alt_time_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_alt_time_str(None))

    def test_angle_parser(self):
        """Checks that angle fields are parsed correctly"""
        expected_inj_1_ang_v2 = self.string_entries["Inj1Angle_v2"][
            "unique_entries"
        ]
        expected_inj_2_ang_v2 = self.string_entries["Inj2Angle_v2"][
            "unique_entries"
        ]
        for example_key, example_val in expected_inj_1_ang_v2.items():
            expected = example_val
            actual = self.blank_model._parse_angle_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_inj_2_ang_v2.items():
            expected = example_val
            actual = self.blank_model._parse_angle_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_angle_str(None))

    def test_current_parser(self):
        """Checks that current fields are parsed correctly"""
        expected_inj_1_cur = self.string_entries["Inj1Current"][
            "unique_entries"
        ]
        expected_inj_2_cur = self.string_entries["Inj2Current"][
            "unique_entries"
        ]
        for example_key, example_val in expected_inj_1_cur.items():
            expected = example_val
            actual = self.blank_model._parse_current_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_inj_2_cur.items():
            expected = example_val
            actual = self.blank_model._parse_current_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_current_str(None))

    def test_length_of_time_parser(self):
        """Checks that length-of-time fields are parsed correctly"""
        expected_inj_1_len_of_time = self.string_entries["Inj1LenghtofTime"][
            "unique_entries"
        ]
        expected_inj_2_len_of_time = self.string_entries["Inj2LenghtofTime"][
            "unique_entries"
        ]
        for example_key, example_val in expected_inj_1_len_of_time.items():
            expected = example_val
            actual = self.blank_model._parse_length_of_time_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_inj_2_len_of_time.items():
            expected = example_val
            actual = self.blank_model._parse_length_of_time_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_length_of_time_str(None))

    def test_volume_parser(self):
        """Checks that volume fields are parsed correctly"""
        expected_inj_1_vol = self.string_entries["Inj1Vol"]["unique_entries"]
        expected_inj_2_vol = self.string_entries["Inj2Vol"]["unique_entries"]
        expected_inj_1_vol_per_depth = self.string_entries["inj1volperdepth"][
            "unique_entries"
        ]
        expected_inj_2_vol_per_depth = self.string_entries["inj2volperdepth"][
            "unique_entries"
        ]
        for example_key, example_val in expected_inj_1_vol.items():
            expected = example_val
            actual = self.blank_model._parse_inj_vol_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_inj_2_vol.items():
            expected = example_val
            actual = self.blank_model._parse_inj_vol_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_inj_1_vol_per_depth.items():
            expected = example_val
            actual = self.blank_model._parse_inj_vol_str(example_key)
            self.assertEqual(expected, actual)
        for example_key, example_val in expected_inj_2_vol_per_depth.items():
            expected = example_val
            actual = self.blank_model._parse_inj_vol_str(example_key)
            self.assertEqual(expected, actual)
        self.assertIsNone(self.blank_model._parse_inj_vol_str(None))


if __name__ == "__main__":
    unittest_main()
