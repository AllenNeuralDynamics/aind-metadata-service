"""Tests NSB 2023 string parsers work against examples"""

import json
import os
from pathlib import Path
from typing import Callable, List
from unittest import TestCase
from unittest import main as unittest_main

from aind_metadata_service.sharepoint.nsb2023.mapping import MappedNSBList
from aind_metadata_service.sharepoint.nsb2023.models import NSBList

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
TEST_EXAMPLES = (
    TEST_DIR
    / "resources"
    / "sharepoint"
    / "nsb2023"
    / "nsb2023_string_entries.json"
)


class TestNSB2023StringParsers(TestCase):
    """Tests text field parsers in NSB2023Mapping class. Certain fields, such
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

    def test_alt_time_parser(self):
        """Checks that alternating time fields are parsed correctly"""

        at_keys = [
            "Inj1AlternatingTime",
            "Inj2AlternatingTime",
            "Inj3AlternatingTime",
            "Inj4AlternatingTime",
        ]
        self._test_parser(at_keys, self.blank_model._parse_alt_time_str)

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
