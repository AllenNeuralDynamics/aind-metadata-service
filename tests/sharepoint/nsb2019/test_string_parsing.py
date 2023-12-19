"""Tests NSB 2019 string parsers work against examples"""

import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Callable, List
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
        cls.blank_model = MappedNSBList(nsb=NSBList.model_construct())

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
                if isinstance(expected, float):
                    expected = Decimal(str(example_val))
                actual = parser(example_key)
                self.assertEqual(expected, actual)
        self.assertIsNone(parser(None))

    def test_ap_parser(self):
        """Checks that ap fields are parsed correctly"""
        ap_keys = ["AP2ndInj", "HP_x0020_A_x002f_P", "Virus_x0020_A_x002f_P"]
        self._test_parser(ap_keys, self.blank_model._parse_ap_str)

    def test_dv_parser(self):
        """Checks that dv fields are parsed correctly"""
        dv_keys = [
            "DV2ndInj",
            "FiberImplant1DV",
            "FiberImplant2DV",
            "Virus_x0020_D_x002f_V",
        ]
        self._test_parser(dv_keys, self.blank_model._parse_dv_str)

    def test_iso_dur_parser(self):
        """Checks that the iso duration fields are parsed correctly"""
        iso_keys = ["FirstInjectionIsoDuration", "SecondInjectionIsoDuration"]
        self._test_parser(iso_keys, self.blank_model._parse_iso_dur_str)

    def test_weight_parser(self):
        """Checks that weight fields are parsed correctly"""
        w_keys = [
            "FirstInjectionWeightAfter",
            "FirstInjectionWeightBefor",
            "Touch_x0020_Up_x0020_Weight_x002",
            "Weight_x0020_after_x0020_Surgery",
            "Weight_x0020_before_x0020_Surger",
            "SecondInjectionWeightAfter",
            "SecondInjectionWeightBefore",
        ]
        self._test_parser(w_keys, self.blank_model._parse_weight_str)

    def test_ml_parser(self):
        """Checks that ml fields are parsed correctly"""

        ml_keys = ["ML2ndInj", "HP_x0020_M_x002f_L", "Virus_x0020_M_x002f_L"]
        self._test_parser(ml_keys, self.blank_model._parse_ml_str)

    def test_alt_time_parser(self):
        """Checks that alternating time fields are parsed correctly"""

        at_keys = ["Inj1AlternatingTime", "Inj2AlternatingTime"]
        self._test_parser(at_keys, self.blank_model._parse_alt_time_str)

    def test_angle_parser(self):
        """Checks that angle fields are parsed correctly"""

        an_keys = ["Inj1Angle_v2", "Inj2Angle_v2"]
        self._test_parser(an_keys, self.blank_model._parse_angle_str)

    def test_current_parser(self):
        """Checks that current fields are parsed correctly"""

        c_keys = ["Inj1Current", "Inj2Current"]
        self._test_parser(c_keys, self.blank_model._parse_current_str)

    def test_length_of_time_parser(self):
        """Checks that length-of-time fields are parsed correctly"""

        lt_keys = ["Inj1LenghtofTime", "Inj2LenghtofTime"]
        self._test_parser(lt_keys, self.blank_model._parse_length_of_time_str)

    def test_volume_parser(self):
        """Checks that volume fields are parsed correctly"""

        v_keys = ["Inj1Vol", "Inj2Vol", "inj1volperdepth", "inj2volperdepth"]
        self._test_parser(v_keys, self.blank_model._parse_inj_vol_str)


if __name__ == "__main__":
    unittest_main()
