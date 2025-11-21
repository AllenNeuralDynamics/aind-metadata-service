"""Tests NSB 2019 data model is parsed correctly"""

import json
import os
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Callable, List
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.components.coordinates import CoordinateSystemLibrary
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema.components.surgery_procedures import (
    BrainInjection,
    Craniotomy,
    Headframe,
    ProbeImplant,
)
from aind_sharepoint_service_async_client.models.nsb2019_list import (
    NSB2019List,
)

from aind_metadata_service_server.mappers.nsb2019 import MappedNSBList

TEST_DIR = Path(__file__).parent / ".."
DIR_RAW = TEST_DIR / "resources" / "nsb2019" / "raw"
TEST_EXAMPLES = (
    TEST_DIR / "resources" / "nsb2019" / "nsb2019_string_entries.json"
)


class TestNSB2019Mappers(TestCase):
    """Tests NSB2019 mapper functionality"""

    def test_map_to_surgeries_basic(self):
        """Test that mapper creates Surgery objects from NSB data"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        # Basic assertions
        self.assertIsInstance(surgeries, list)
        self.assertGreater(len(surgeries), 0)
        
        for surgery in surgeries:
            self.assertIsInstance(surgery, Surgery)
            # All surgeries should have start date
            # self.assertIsNotNone(surgery.start_date)
            # All surgeries should have experimenters
            self.assertIsNotNone(surgery.experimenters)
            self.assertGreater(len(surgery.experimenters), 0)

    def test_map_to_surgeries_with_injection(self):
        """Test that injection procedures are created correctly"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        # Check for injection procedures
        injection_surgeries = [
            s for s in surgeries
            if any(isinstance(p, BrainInjection) for p in s.procedures)
        ]
        self.assertGreater(len(injection_surgeries), 0)
        
        # Verify injection has required fields
        for surgery in injection_surgeries:
            for proc in surgery.procedures:
                if isinstance(proc, BrainInjection):
                    self.assertIsNotNone(proc.object_type)
                    self.assertEqual(proc.object_type, "Brain injection")

    def test_map_to_surgeries_with_headframe(self):
        """Test that headframe procedures are created correctly"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        # Check for headframe procedures
        headframe_surgeries = [
            s for s in surgeries
            if any(isinstance(p, Headframe) for p in s.procedures)
        ]
        
        if len(headframe_surgeries) > 0:
            for surgery in headframe_surgeries:
                for proc in surgery.procedures:
                    if isinstance(proc, Headframe):
                        self.assertIsNotNone(proc.object_type)
                        self.assertEqual(proc.object_type, "Headframe")

    def test_map_to_surgeries_with_craniotomy(self):
        """Test that craniotomy procedures are created correctly"""
        with open(DIR_RAW / "list_item2.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        # Check for craniotomy procedures
        craniotomy_surgeries = [
            s for s in surgeries
            if any(isinstance(p, Craniotomy) for p in s.procedures)
        ]
        
        if len(craniotomy_surgeries) > 0:
            for surgery in craniotomy_surgeries:
                for proc in surgery.procedures:
                    if isinstance(proc, Craniotomy):
                        self.assertIsNotNone(proc.object_type)
                        self.assertIsNotNone(proc.craniotomy_type)

    def test_map_to_surgeries_with_fiber_implant(self):
        """Test that fiber implant procedures are created correctly"""
        # Find a file with fiber implant data
        for filename in os.listdir(DIR_RAW):
            with open(DIR_RAW / filename) as f:
                raw_data = json.load(f)
            
            nsb_model = NSB2019List.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            
            if mapper.has_fiber_implant_procedure:
                surgeries = mapper.get_surgeries()
                
                # Check for probe implant procedures
                probe_surgeries = [
                    s for s in surgeries
                    if any(isinstance(p, ProbeImplant) for p in s.procedures)
                ]
                
                self.assertGreater(len(probe_surgeries), 0)
                
                for surgery in probe_surgeries:
                    for proc in surgery.procedures:
                        if isinstance(proc, ProbeImplant):
                            self.assertIsNotNone(proc.implanted_device)
                break

    def test_map_experimenter_name(self):
        """Test that experimenter name is formatted correctly"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        experimenter_name = mapper.aind_experimenter_full_name
        self.assertIsNotNone(experimenter_name)
        self.assertTrue(experimenter_name.startswith("NSB"))

    def test_map_iacuc_protocol(self):
        """Test that IACUC protocol is mapped correctly"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        for surgery in surgeries:
            if surgery.ethics_review_id:
                # Should be a string like "2001", "2002", etc.
                self.assertIsInstance(surgery.ethics_review_id, str)

    def test_map_anaesthesia_info(self):
        """Test that anaesthesia information is mapped correctly"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        for surgery in surgeries:
            if surgery.anaesthesia:
                self.assertIsNotNone(surgery.anaesthesia.anaesthetic_type)
                self.assertEqual(surgery.anaesthesia.anaesthetic_type, "isoflurane")

    def test_map_coordinate_systems(self):
        """Test that coordinate systems are assigned correctly"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        # Check that surgeries with procedures have coordinate systems
        for surgery in surgeries:
            for proc in surgery.procedures:
                if isinstance(proc, BrainInjection) and proc.coordinate_system_name:
                    self.assertIsInstance(proc.coordinate_system_name, str)
                    self.assertIn("BREGMA", proc.coordinate_system_name.upper())

    def test_properties_count(self):
        """Tests that the correct number of properties are parsed"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        props = []
        for k in dir(mapper.__class__):
            cls = mapper.__class__
            attr = getattr(cls, k)
            if isinstance(attr, property):
                props.append(getattr(mapper, k))
        self.assertEqual(85, len(props))

    def test_injection_mapping_edge_cases(self):
        """Tests edge cases for injection procedure mapping"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        # Malformed injection types should still create BrainInjection
        raw_data["Inj1Type"] = "Select..."
        raw_data["Inj2Type"] = "Nanoject (Pressure)"
        raw_data["Procedure"] = "Stereotaxic Injection"
        raw_data["Virus_x0020_A_x002f_P"] = "3 lambda"
        raw_data["AP2ndInj"] = "2 lambda"
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        self.assertGreater(len(surgeries), 0)
        procedures = surgeries[1].procedures if len(surgeries) > 1 else surgeries[0].procedures
        self.assertTrue(any(isinstance(p, BrainInjection) for p in procedures))
        
        # Test with both types as "Select..."
        raw_data["Inj2Type"] = "Select..."
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        procedures = surgeries[0].procedures
        self.assertTrue(any(isinstance(p, BrainInjection) for p in procedures))

    def test_inj2_coordinates_reference_edge_cases(self):
        """Test edge cases for second injection coordinate reference"""
        nsb_data_1 = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "AP2ndInj": "1.0",
            "ML2ndInj": "2.0",
            "DV2ndInj": None,
        }
        nsb_model_1 = NSB2019List.model_validate(nsb_data_1)
        mapper_1 = MappedNSBList(nsb=nsb_model_1)
        
        self.assertEqual(
            mapper_1.aind_inj2_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARI,
        )
        
        # Test with all None values
        nsb_data_2 = {
            "FileSystemObjectType": 0,
            "Id": 2,
            "AP2ndInj": None,
            "ML2ndInj": None,
            "DV2ndInj": None,
        }
        nsb_model_2 = NSB2019List.model_validate(nsb_data_2)
        mapper_2 = MappedNSBList(nsb=nsb_model_2)
        
        self.assertIsNone(mapper_2.aind_inj2_coordinates_reference)

    def test_unknown_surgery_edge_case(self):
        """Test handling of unknown surgery types"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        raw_data["Procedure"] = None
        raw_data["Date_x0020_of_x0020_Surgery"] = None
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        self.assertEqual(len(surgeries), 0)

    def test_get_measured_coordinates_edge_case(self):
        """Test measured coordinates with None values"""
        coords = MappedNSBList.get_measured_coordinates(
            b2l_dist=None, coordinate_system_name=None
        )
        self.assertIsNone(coords)
        
        # Test with valid bregma-lambda distance
        coords = MappedNSBList.get_measured_coordinates(
            b2l_dist=Decimal("4.5"), coordinate_system_name="BREGMA_ARI"
        )
        self.assertIsNotNone(coords)

    # def test_all_raw_files_parse_successfully(self):
    #     """Test that all raw NSB files can be parsed without errors"""
    #     for filename in os.listdir(DIR_RAW):
    #         with self.subTest(file=filename):
    #             with open(DIR_RAW / filename) as f:
    #                 raw_data = json.load(f)
                
    #             nsb_model = NSB2019List.model_validate(raw_data)
    #             mapper = MappedNSBList(nsb=nsb_model)
    #             surgeries = mapper.get_surgeries()
                
    #             # Basic structural validations
    #             self.assertIsInstance(surgeries, list)
    #             for surgery in surgeries:
    #                 self.assertIsInstance(surgery, Surgery)
    #                 # self.assertIsNotNone(surgery.start_date)
    #                 # self.assertIsInstance(surgery.procedures, list)


class TestNSB2019StringParsers(TestCase):
    """Tests text field parsers in NSB2019Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Load string entry examples and build a blank mapper"""
        with open(TEST_EXAMPLES, encoding="utf-8") as f:
            cls.string_entries = json.load(f)
        
        # Create minimal valid NSB model for testing parsers
        cls.blank_model = MappedNSBList(
            nsb=NSB2019List.model_validate(
                {"FileSystemObjectType": 0, "Id": 0}
            )
        )

    def _test_parser(self, keys: List[str], parser: Callable) -> None:
        """Run a list of example keys through one of the _parse_* methods"""
        for field in keys:
            entries = self.string_entries[field]["unique_entries"]
            for raw_input, expected in entries.items():
                if isinstance(expected, float):
                    expected = Decimal(str(expected))
                actual = parser(raw_input)
                self.assertEqual(expected, actual, f"{field}: {raw_input!r}")
        self.assertIsNone(parser(None))

    def test_ap_parser(self):
        """Tests parsing of AP coordinate values"""
        ap_keys = ["AP2ndInj", "HP_x0020_A_x002f_P", "Virus_x0020_A_x002f_P"]
        self._test_parser(ap_keys, self.blank_model._parse_ap_str)

    def test_dv_parser(self):
        """Tests parsing of DV coordinate values"""
        dv_keys = [
            "DV2ndInj",
            "FiberImplant1DV",
            "FiberImplant2DV",
            "Virus_x0020_D_x002f_V",
        ]
        self._test_parser(dv_keys, self.blank_model._parse_dv_str)

    def test_ml_parser(self):
        """Tests parsing of ML coordinate values"""
        ml_keys = ["ML2ndInj", "HP_x0020_M_x002f_L", "Virus_x0020_M_x002f_L"]
        self._test_parser(ml_keys, self.blank_model._parse_ml_str)

    def test_iso_dur_parser(self):
        """Tests parsing of isoflurane duration values"""
        iso_keys = ["FirstInjectionIsoDuration", "SecondInjectionIsoDuration"]
        self._test_parser(iso_keys, self.blank_model._parse_iso_dur_str)

    def test_weight_parser(self):
        """Tests parsing of animal weight values"""
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

    def test_alt_time_parser(self):
        """Tests parsing of alternating time values"""
        at_keys = ["Inj1AlternatingTime", "Inj2AlternatingTime"]
        self._test_parser(at_keys, self.blank_model._parse_alt_time_str)

    def test_angle_parser(self):
        """Tests parsing of injection angle values"""
        an_keys = ["Inj1Angle_v2", "Inj2Angle_v2"]
        self._test_parser(an_keys, self.blank_model._parse_angle_str)

    def test_current_parser(self):
        """Tests parsing of injection current values"""
        c_keys = ["Inj1Current", "Inj2Current"]
        self._test_parser(c_keys, self.blank_model._parse_current_str)

    def test_length_of_time_parser(self):
        """Tests parsing of duration/length of time values"""
        lt_keys = ["Inj1LenghtofTime", "Inj2LenghtofTime"]
        self._test_parser(lt_keys, self.blank_model._parse_length_of_time_str)

    def test_volume_parser(self):
        """Tests parsing of injection volume values"""
        v_keys = ["Inj1Vol", "Inj2Vol", "inj1volperdepth", "inj2volperdepth"]
        self._test_parser(v_keys, self.blank_model._parse_inj_vol_str)

    def test_basic_float_parser(self):
        """Tests parsing of basic float strings"""
        self.assertEqual(
            self.blank_model._parse_basic_float_str("1.5"),
            1.5
        )
        self.assertEqual(
            self.blank_model._parse_basic_float_str("0"),
            0.0
        )
        self.assertIsNone(self.blank_model._parse_basic_float_str("invalid"))
        self.assertIsNone(self.blank_model._parse_basic_float_str(None))

    def test_basic_decimal_parser(self):
        """Tests parsing of basic decimal strings"""
        self.assertEqual(
            self.blank_model._parse_basic_decimal_str("1.5"),
            Decimal("1.5")
        )
        self.assertEqual(
            self.blank_model._parse_basic_decimal_str("0"),
            Decimal("0")
        )
        self.assertIsNone(self.blank_model._parse_basic_decimal_str("invalid"))
        self.assertIsNone(self.blank_model._parse_basic_decimal_str(None))


if __name__ == "__main__":
    unittest_main()
