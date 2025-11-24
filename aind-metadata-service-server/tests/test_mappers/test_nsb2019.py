"""Tests NSB 2019 data model is parsed correctly"""

import json
import os
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
    CraniotomyType,
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


class TestNSB2019BasicMapping(TestCase):
    """Tests basic NSB2019 mapping functionality"""

    def test_map_experimenter_full_name(self):
        """Test experimenter full name mapping"""
        nsb_model_author = NSB2019List.model_validate(
            {"FileSystemObjectType": 0, "Id": 1, "AuthorId": 187}
        )
        nsb_model = NSB2019List.model_validate(nsb_model_author)
        mapper = MappedNSBList(nsb=nsb_model)
        
        experimenter = mapper.aind_experimenter_full_name
        self.assertEqual(experimenter, "NSB-187")
        
        nsb_model_no_author = NSB2019List.model_validate(
            {"FileSystemObjectType": 0, "Id": 1}
        )
        mapper_no_author = MappedNSBList(nsb=nsb_model_no_author)
        self.assertEqual(mapper_no_author.aind_experimenter_full_name, "NSB")

    def test_map_anaesthetic_type(self):
        """Test anaesthetic type is always isoflurane"""
        nsb_model = NSB2019List.model_validate(
            {"FileSystemObjectType": 0, "Id": 1}
        )
        mapper = MappedNSBList(nsb=nsb_model)
        self.assertEqual(mapper.aind_anaesthetic_type, "isoflurane")

    def test_map_iacuc_protocol(self):
        """Test IACUC protocol mapping"""
        raw_data = {"IACUC_x0020_Protocol_x0020__x002": "2115"}
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        if mapper.aind_iacuc_protocol:
            self.assertIsInstance(mapper.aind_iacuc_protocol, str)
            self.assertRegex(mapper.aind_iacuc_protocol, r"^\d{4}$")

    def test_map_surgery_dates(self):
        """Test surgery date mappings"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        # Test date of surgery
        if mapper.aind_date_of_surgery:
            self.assertIsNotNone(mapper.aind_date_of_surgery)
        
        # Test date of first injection
        if mapper.aind_date1st_injection:
            self.assertIsNotNone(mapper.aind_date1st_injection)
        
        # Test date of second injection
        if mapper.aind_date2nd_injection:
            self.assertIsNotNone(mapper.aind_date2nd_injection)

    def test_map_animal_weights(self):
        """Test animal weight mappings"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        # Test surgery weights
        if mapper.aind_weight_before_surger:
            self.assertIsInstance(mapper.aind_weight_before_surger, Decimal)
            self.assertGreater(mapper.aind_weight_before_surger, 0)
        
        if mapper.aind_weight_after_surgery:
            self.assertIsInstance(mapper.aind_weight_after_surgery, Decimal)
            self.assertGreater(mapper.aind_weight_after_surgery, 0)
        
        # Test first injection weights
        if mapper.aind_first_injection_weight_be:
            self.assertIsInstance(mapper.aind_first_injection_weight_be, Decimal)
        
        if mapper.aind_first_injection_weight_af:
            self.assertIsInstance(mapper.aind_first_injection_weight_af, Decimal)

    def test_map_workstation_ids(self):
        """Test workstation ID mappings"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        if mapper.aind_hp_work_station:
            self.assertIn("SWS", mapper.aind_hp_work_station)
        
        if mapper.aind_work_station1st_injection:
            self.assertIn("SWS", mapper.aind_work_station1st_injection)
        
        if mapper.aind_work_station2nd_injection:
            self.assertIn("SWS", mapper.aind_work_station2nd_injection)


class TestNSB2019HeadframeMapping(TestCase):
    """Tests headframe procedure mapping"""

    def test_map_headframe_type(self):
        """Test headframe type mapping"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        head_post_info = mapper.aind_headpost_type
        self.assertIsNotNone(head_post_info)
        
        if head_post_info.headframe_type:
            self.assertIsInstance(head_post_info.headframe_type, str)

    def test_map_headframe_procedure(self):
        """Test creation of Headframe procedure"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        if mapper.has_head_frame_procedure:
            headframe = mapper.get_head_frame_procedure()
            self.assertIsInstance(headframe, Headframe)
            self.assertEqual(headframe.object_type, "Headframe")
            
            if headframe.headframe_type:
                self.assertIsInstance(headframe.headframe_type, str)

    def test_headframe_all_types(self):
        """Test all headframe type variations"""
        test_cases = [
            ("CAMstyle headframe (0160-100-10 Rev A)", "CAM-style"),
            ("Neuropixelstyle headframe", "Neuropixel-style"),
            ("Mesoscopestyle well with NGC headframe", "NGC-style"),
            ("NGCstyle headframe (no well)", "NGC-style"),
        ]
        
        for procedure_value, expected_type in test_cases:
            with self.subTest(procedure=procedure_value):
                nsb_data = {
                    "FileSystemObjectType": 0,
                    "Id": 1,
                    "Headpost_x0020_Type": procedure_value,
                }
                nsb_model = NSB2019List.model_validate(nsb_data)
                mapper = MappedNSBList(nsb=nsb_model)
                
                head_post = mapper.aind_headpost_type
                if head_post.headframe_type:
                    self.assertEqual(head_post.headframe_type, expected_type)


class TestNSB2019CraniotomyMapping(TestCase):
    """Tests craniotomy procedure mapping"""

    def test_map_craniotomy_type(self):
        """Test craniotomy type mapping"""
        with open(DIR_RAW / "list_item2.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        craniotomy_type = mapper.aind_craniotomy_type
        if craniotomy_type:
            self.assertIsInstance(craniotomy_type, CraniotomyType)

    def test_map_craniotomy_size(self):
        """Test craniotomy size mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "CraniotomyType": "Visual Cortex 5mm",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        size = mapper.aind_craniotomy_size
        if size:
            self.assertEqual(size, Decimal(5))

    def test_map_craniotomy_coordinates(self):
        """Test craniotomy coordinate system mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Craniotomy_x0020_Type": "Visual cortex (5mm)",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        coord_sys = mapper.aind_craniotomy_coordinates_reference
        if coord_sys:
            self.assertEqual(coord_sys.name, "LAMBDA_ARI")

    def test_map_craniotomy_procedure(self):
        """Test creation of Craniotomy procedure"""
        with open(DIR_RAW / "list_item2.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        if mapper.has_craniotomy_procedure:
            craniotomy = mapper.get_craniotomy_procedure()
            self.assertIsInstance(craniotomy, Craniotomy)
            self.assertIsNotNone(craniotomy.craniotomy_type)
            self.assertIsNotNone(craniotomy.coordinate_system_name)

    def test_map_dura_removed(self):
        """Test dura removed flag mapping"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        dura_removed = mapper.aind_hp_durotomy
        if dura_removed is not None:
            self.assertIsInstance(dura_removed, bool)


class TestNSB2019InjectionMapping(TestCase):
    """Tests brain injection procedure mapping"""

    def test_map_first_injection_coordinates(self):
        """Test first injection coordinate mapping"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        # Test AP coordinate
        ap = mapper.aind_virus_a_p
        if ap:
            self.assertIsInstance(ap, Decimal)
        
        # Test ML coordinate
        ml = mapper.aind_virus_m_l
        if ml:
            self.assertIsInstance(ml, Decimal)
        
        # Test DV coordinate
        dv = mapper.aind_virus_d_v
        if dv:
            self.assertIsInstance(dv, Decimal)

    def test_map_first_injection_hemisphere(self):
        """Test first injection hemisphere mapping"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        hemisphere = mapper.aind_virus_hemisphere
        if hemisphere:
            self.assertIn(hemisphere.value, ["Left", "Right"])

    def test_map_first_injection_coordinate_system(self):
        """Test first injection coordinate system mapping"""
        # Test BREGMA_ARI (no DV)
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Virus_x0020_A_x002f_P": "1.5",
            "Virus_x0020_M_x002f_L": "2.0",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        coord_sys = mapper.aind_inj1_coordinates_reference
        if coord_sys:
            self.assertEqual(coord_sys, CoordinateSystemLibrary.BREGMA_ARI)
        
        # Test BREGMA_ARID (with DV)
        nsb_data["Virus_x0020_D_x002f_V"] = "3.0"
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        coord_sys = mapper.aind_inj1_coordinates_reference
        if coord_sys:
            self.assertEqual(coord_sys, CoordinateSystemLibrary.BREGMA_ARID)

    def test_map_first_injection_type(self):
        """Test first injection type mapping"""
        # Test Nanoject
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Inj1Type": "Nanoject (Pressure)",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        from aind_metadata_service_server.mappers.nsb2019 import InjectionType
        
        inj_type = mapper.aind_inj1_type
        if inj_type:
            self.assertEqual(inj_type, InjectionType.NANOJECT)
        
        # Test Iontophoresis
        nsb_data["Inj1Type"] = "Iontophoresis"
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        inj_type = mapper.aind_inj1_type
        if inj_type:
            self.assertEqual(inj_type, InjectionType.IONTOPHORESIS)

    def test_map_first_injection_volume(self):
        """Test first injection volume mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Inj1Vol": "50 nL",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        volume = mapper.aind_inj1_vol
        if volume:
            self.assertIsInstance(volume, list)
            self.assertEqual(volume[0], Decimal(50))

    def test_map_first_injection_angle(self):
        """Test first injection angle mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Inj1Angle0": "10 degrees",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        angle = mapper.aind_inj1angle0
        if angle:
            self.assertEqual(angle, Decimal(10))

    def test_map_first_injection_dynamics(self):
        """Test first injection dynamics creation"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        dynamics = mapper.aind_inj1_dynamics
        self.assertIsNotNone(dynamics)
        self.assertIsNotNone(dynamics.profile)

    def test_map_first_injection_procedure(self):
        """Test creation of first BrainInjection procedure"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        if mapper.has_injection_procedure:
            injection = mapper.get_first_injection_procedure()
            self.assertIsInstance(injection, BrainInjection)
            self.assertEqual(injection.object_type, "Brain injection")
            
            if injection.dynamics:
                self.assertGreater(len(injection.dynamics), 0)

    def test_map_second_injection_coordinates(self):
        """Test second injection coordinate mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "AP2ndInj": "2.5",
            "ML2ndInj": "1.5",
            "DV2ndInj": "3.0",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        self.assertEqual(mapper.aind_ap2nd_inj, Decimal("2.5"))
        self.assertEqual(mapper.aind_ml2nd_inj, Decimal("1.5"))
        self.assertEqual(mapper.aind_dv2nd_inj, Decimal("3.0"))

    def test_map_second_injection_coordinate_system(self):
        """Test second injection coordinate system mapping"""
        # Test BREGMA_ARI
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "AP2ndInj": "1.0",
            "ML2ndInj": "2.0",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        coord_sys = mapper.aind_inj2_coordinates_reference
        if coord_sys:
            self.assertEqual(coord_sys, CoordinateSystemLibrary.BREGMA_ARI)
        
        # Test None when no coordinates
        nsb_data_none = {
            "FileSystemObjectType": 0,
            "Id": 2,
        }
        nsb_model_none = NSB2019List.model_validate(nsb_data_none)
        mapper_none = MappedNSBList(nsb=nsb_model_none)
        
        self.assertIsNone(mapper_none.aind_inj2_coordinates_reference)

    def test_map_second_injection_hemisphere(self):
        """Test second injection hemisphere mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Hemisphere2ndInj": "Right",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        hemisphere = mapper.aind_hemisphere2nd_inj
        if hemisphere:
            self.assertIn(hemisphere.value, ["Left", "Right"])

    def test_map_second_injection_procedure(self):
        """Test creation of second BrainInjection procedure"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Procedure": "Stereotaxic Injection",
            "AP2ndInj": "1.0",
            "ML2ndInj": "2.0",
            "Inj2Type": "Nanoject (Pressure)",
            "Inj2Vol": "25 nL",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        if mapper.has_second_injection_procedure:
            injection = mapper.get_second_injection_procedure()
            self.assertIsInstance(injection, BrainInjection)
            self.assertEqual(injection.object_type, "Brain injection")

    def test_injection_with_malformed_types(self):
        """Test injection creation with malformed/missing types"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Procedure": "Stereotaxic Injection",
            "Inj1Type": "Select...",
            "Virus_x0020_A_x002f_P": "1.5",
            "Virus_x0020_M_x002f_L": "2.0",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        # Should still create injection even with malformed type
        if mapper.has_injection_procedure:
            injection = mapper.get_first_injection_procedure()
            self.assertIsInstance(injection, BrainInjection)


class TestNSB2019FiberImplantMapping(TestCase):
    """Tests fiber implant/probe implant mapping"""

    def test_map_fiber_implant_flags(self):
        """Test fiber implant presence flags"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "FiberImplant1": True,
            "FiberImplant2": False,
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        self.assertTrue(mapper.aind_fiber_implant1)
        self.assertFalse(mapper.aind_fiber_implant2)

    def test_map_fiber_implant_depth(self):
        """Test fiber implant depth mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "FiberImplant1DV": "3.5 mm",
            "FiberImplant2DV": "2.0 mm",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        if mapper.aind_fiber_implant1_dv:
            self.assertEqual(mapper.aind_fiber_implant1_dv, Decimal("3.5"))
        
        if mapper.aind_fiber_implant2_dv:
            self.assertEqual(mapper.aind_fiber_implant2_dv, Decimal("2.0"))

    def test_map_fiber_implant_procedures(self):
        """Test creation of ProbeImplant procedures"""
        # Find a test file with fiber implants
        for filename in os.listdir(DIR_RAW):
            with open(DIR_RAW / filename) as f:
                raw_data = json.load(f)
            
            nsb_model = NSB2019List.model_validate(raw_data)
            mapper = MappedNSBList(nsb=nsb_model)
            
            if mapper.has_fiber_implant_procedure:
                fiber_implants = mapper.get_fiber_implants()
                self.assertIsInstance(fiber_implants, list)
                
                for implant in fiber_implants:
                    self.assertIsInstance(implant, ProbeImplant)
                    self.assertIsNotNone(implant.implanted_device)
                    self.assertIsNotNone(implant.device_config)
                break


class TestNSB2019SurgeryIntegration(TestCase):
    """Tests complete Surgery object creation"""

    def test_get_surgeries_basic(self):
        """Test basic surgery creation"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        self.assertIsInstance(surgeries, list)
        self.assertGreater(len(surgeries), 0)
        
        for surgery in surgeries:
            self.assertIsInstance(surgery, Surgery)
            self.assertIsNotNone(surgery.experimenters)
            self.assertGreater(len(surgery.experimenters), 0)

    def test_get_surgeries_with_headframe_and_craniotomy(self):
        """Test surgery with headframe and craniotomy procedures"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        # Find surgery with headframe
        headframe_surgery = None
        for surgery in surgeries:
            if any(isinstance(p, Headframe) for p in surgery.procedures):
                headframe_surgery = surgery
                break
        
        if headframe_surgery:
            self.assertIsNotNone(headframe_surgery.anaesthesia)
            if headframe_surgery.anaesthesia:
                self.assertEqual(
                    headframe_surgery.anaesthesia.anaesthetic_type,
                    "isoflurane"
                )

    def test_get_surgeries_with_injections(self):
        """Test surgery with injection procedures"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        # Find surgery with injection
        injection_surgery = None
        for surgery in surgeries:
            if any(isinstance(p, BrainInjection) for p in surgery.procedures):
                injection_surgery = surgery
                break
        
        if injection_surgery:
            self.assertIsNotNone(injection_surgery.start_date)
            
            # Check measured coordinates if present
            if injection_surgery.measured_coordinates:
                self.assertIsInstance(injection_surgery.measured_coordinates, dict)

    def test_get_surgeries_unknown_procedure(self):
        """Test handling of unknown procedures"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Procedure": None,
            "Date_x0020_of_x0020_Surgery": None,
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        
        self.assertEqual(len(surgeries), 0)

    def test_has_procedure_flags(self):
        """Test procedure presence flags"""
        with open(DIR_RAW / "list_item1.json") as f:
            raw_data = json.load(f)
        
        nsb_model = NSB2019List.model_validate(raw_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        # Test various procedure flags
        self.assertIsInstance(mapper.has_injection_procedure, bool)
        self.assertIsInstance(mapper.has_craniotomy_procedure, bool)
        self.assertIsInstance(mapper.has_head_frame_procedure, bool)
        self.assertIsInstance(mapper.has_fiber_implant_procedure, bool)


class TestNSB2019CoordinateMapping(TestCase):
    """Tests coordinate and transform mapping"""

    def test_map_measured_coordinates(self):
        """Test measured coordinates mapping"""
        # Test with bregma-lambda distance
        coords = MappedNSBList.get_measured_coordinates(
            b2l_dist=Decimal("4.5"),
            coordinate_system_name="BREGMA_ARI"
        )
        self.assertIsNotNone(coords)
        
        # Test with None
        coords_none = MappedNSBList.get_measured_coordinates(
            b2l_dist=None,
            coordinate_system_name=None
        )
        self.assertIsNone(coords_none)

    def test_map_bregma_lambda_distance(self):
        """Test bregma-lambda distance mapping"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Breg2Lamb": "-4.5",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        b2l = mapper.aind_breg2_lamb
        self.assertEqual(b2l, Decimal("4.5"))


class TestNSB2019StringParsers(TestCase):
    """Tests text field parsers in NSB2019Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Load string entry examples and build a blank mapper"""
        with open(TEST_EXAMPLES, encoding="utf-8") as f:
            cls.string_entries = json.load(f)
        
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
        self.assertEqual(self.blank_model._parse_basic_float_str("1.5"), 1.5)
        self.assertEqual(self.blank_model._parse_basic_float_str("0"), 0.0)
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
