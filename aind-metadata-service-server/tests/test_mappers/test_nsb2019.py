"""Tests NSB 2019 data model is parsed correctly"""

import json
import logging
import os
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Callable, List, Tuple
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.core.procedures import BrainInjection
from aind_sharepoint_service_async_client.models.nsb2019_list import (
    NSB2019List,
)

from aind_metadata_service_server.mappers.nsb2019 import MappedNSBList

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(__file__).parent / ".."
DIR_RAW = TEST_DIR / "resources" / "nsb2019" / "raw"
DIR_MAP = TEST_DIR / "resources" / "nsb2019" / "mapped"
LIST_ITEM_FILE_NAMES = os.listdir(DIR_RAW)
sorted(LIST_ITEM_FILE_NAMES)
LIST_ITEM_FILE_PATHS = [DIR_RAW / f for f in LIST_ITEM_FILE_NAMES]
MAPPED_ITEM_FILE_NAMES = os.listdir(DIR_MAP)
sorted(MAPPED_ITEM_FILE_NAMES)
MAPPED_FILE_PATHS = [DIR_MAP / f for f in MAPPED_ITEM_FILE_NAMES]
TEST_EXAMPLES = (
    TEST_DIR / "resources" / "nsb2019" / "nsb2019_string_entries.json"
)


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
            expected_mapped_data = list_item[1]
            raw_file_name = list_item[2]
            logging.debug(f"Processing file: {raw_file_name}")
            nsb_model = NSB2019List.model_validate(raw_data)
            mapped_model = MappedNSBList(nsb=nsb_model)
            mapped_procedure = mapped_model.get_surgeries()
            mapped_procedure_json = [
                model.model_dump_json() for model in mapped_procedure
            ]
            mapped_procedure_json_parsed = [
                json.loads(json_str) for json_str in mapped_procedure_json
            ]
            self.assertEqual(
                expected_mapped_data, mapped_procedure_json_parsed
            )

    def test_properties(self):
        """Tests that the properties are parsed correctly."""
        list_item = self.list_items[0]
        raw_data = deepcopy(list_item[0])
        nsb_model = NSB2019List.model_validate(raw_data)
        mapped_model = MappedNSBList(nsb=nsb_model)
        props = []
        for k in dir(mapped_model.__class__):
            cls = mapped_model.__class__
            attr = getattr(cls, k)
            if isinstance(attr, property):
                props.append(getattr(mapped_model, k))
        self.assertEqual(118, len(props))

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
        # raw_data["ImplantIDCoverslipType"] = "3.5"
        # TODO: add ^ check back once we update enum validator
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        mapped_procedure = mapper.get_surgeries()
        procedures = mapped_procedure[1].procedures
        self.assertTrue(isinstance(procedures[0], BrainInjection))
        raw_data["Inj2Type"] = "Select..."
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        mapped_procedure = mapper.get_surgeries()
        procedures = mapped_procedure[0].procedures
        self.assertTrue(isinstance(procedures[0], BrainInjection))
        self.assertIsNone(mapper._parse_basic_float_str("one"))

    def test_unknown_surgery_edge_case(self):
        """Tests the case where there is an unknown surgery type."""
        list_item = self.list_items[0]
        raw_data = deepcopy(list_item[0])
        raw_data["Procedure"] = None
        raw_data["Date_x0020_of_x0020_Surgery"] = None
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        mapped_procedure = mapper.get_surgeries()
        self.assertEqual(len(mapped_procedure), 0)


class TestNSB2019StringParsers(TestCase):
    """Tests text field parsers in NSB2019Mapping class."""

    @classmethod
    def setUpClass(cls):
        """Load string‐entry examples and build a blank mapper."""
        with open(TEST_EXAMPLES, encoding="utf-8") as f:
            cls.string_entries = json.load(f)
        cls.blank_model = MappedNSBList(nsb=NSB2019List.model_construct())

    def _test_parser(self, keys: List[str], parser: Callable) -> None:
        """Run a list of example keys through one of the _parse_* methods."""
        for field in keys:
            entries = self.string_entries[field]["unique_entries"]
            for raw_input, expected in entries.items():
                if isinstance(expected, float):
                    expected = Decimal(str(expected))
                actual = parser(raw_input)
                self.assertEqual(expected, actual, f"{field}: {raw_input!r}")
        self.assertIsNone(parser(None))

    def test_ap_parser(self):
        """Tests parsing of AP values"""
        ap_keys = ["AP2ndInj", "HP_x0020_A_x002f_P", "Virus_x0020_A_x002f_P"]
        self._test_parser(ap_keys, self.blank_model._parse_ap_str)

    def test_dv_parser(self):
        """Tests parsing of DV values"""
        dv_keys = [
            "DV2ndInj",
            "FiberImplant1DV",
            "FiberImplant2DV",
            "Virus_x0020_D_x002f_V",
        ]
        self._test_parser(dv_keys, self.blank_model._parse_dv_str)

    def test_iso_dur_parser(self):
        """Tests parsing of Iso Duration values"""
        iso_keys = ["FirstInjectionIsoDuration", "SecondInjectionIsoDuration"]
        self._test_parser(iso_keys, self.blank_model._parse_iso_dur_str)

    def test_weight_parser(self):
        """Tests parsing of weight values"""
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
        """Tests parsing of ml values"""
        ml_keys = ["ML2ndInj", "HP_x0020_M_x002f_L", "Virus_x0020_M_x002f_L"]
        self._test_parser(ml_keys, self.blank_model._parse_ml_str)

    def test_alt_time_parser(self):
        """Tests parsing of alternating time values"""
        at_keys = ["Inj1AlternatingTime", "Inj2AlternatingTime"]
        self._test_parser(at_keys, self.blank_model._parse_alt_time_str)

    def test_angle_parser(self):
        """Tests parsing of angle values"""
        an_keys = ["Inj1Angle_v2", "Inj2Angle_v2"]
        self._test_parser(an_keys, self.blank_model._parse_angle_str)

    def test_current_parser(self):
        """Tests parsing of current values"""
        c_keys = ["Inj1Current", "Inj2Current"]
        self._test_parser(c_keys, self.blank_model._parse_current_str)

    def test_length_of_time_parser(self):
        """Tests parsing of length of time values"""
        lt_keys = ["Inj1LenghtofTime", "Inj2LenghtofTime"]
        self._test_parser(lt_keys, self.blank_model._parse_length_of_time_str)

    def test_volume_parser(self):
        """Tests parsing of volume values"""
        v_keys = ["Inj1Vol", "Inj2Vol", "inj1volperdepth", "inj2volperdepth"]
        self._test_parser(v_keys, self.blank_model._parse_inj_vol_str)


if __name__ == "__main__":
    unittest_main()
