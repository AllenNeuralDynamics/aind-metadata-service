"""Tests NSB 2023 data model is parsed correctly"""

from copy import deepcopy
from decimal import Decimal
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.components.coordinates import (
    Axis,
    AxisName,
    CoordinateSystem,
    CoordinateSystemLibrary,
    Direction,
)
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema.components.surgery_procedures import (
    BrainInjection,
    Craniotomy,
    CraniotomyType,
    Headframe,
)
from aind_data_schema_models.brain_atlas import BrainStructureModel
from aind_data_schema_models.coordinates import Origin
from aind_sharepoint_service_async_client.models.nsb2023_list import (
    NSB2023List,
)
from aind_data_schema.components.configs import ProbeConfig
from aind_data_schema.components.devices import FiberProbe
from aind_data_schema.components.surgery_procedures import ProbeImplant
from aind_data_schema.components.coordinates import Translation

from aind_metadata_service_server.mappers.nsb2023 import (
    BurrHoleProcedure,
    During,
    HeadPost,
    HeadPostType,
    InjectionType,
    FiberType,
    MappedNSBList,
    HeadPostInfo,
    HeadframeMaterial
)
from aind_data_schema_models.units import SizeUnit

class TestNSB2023BasicMapping(TestCase):
    """Tests basic NSB2023 mapping functionality"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.basic_nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Date_x0020_of_x0020_Surgery": "2022-01-03",
            "Weight_x0020_before_x0020_Surger": 25.2,
            "Weight_x0020_after_x0020_Surgery": 28.2,
            "HpWorkStation": "SWS 4",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
            "Breg2Lamb": -4.5,
            "Protocol": "2119 - Training and qualification of animal users"
        }
        cls.nsb_model = NSB2023List.model_validate(cls.basic_nsb_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_experimenter_full_name(self):
        """Test experimenter name mapping"""
        name = MappedNSBList.aind_experimenter_full_name("2846")
        no_name = MappedNSBList.aind_experimenter_full_name(None)
        self.assertEqual(name, "NSB-2846")
        self.assertEqual(no_name, "NSB")

    def test_map_iacuc_protocol(self):
        """Test IACUC protocol mapping"""
        self.assertEqual("2103", self.mapper.aind_iacuc_protocol)
        self.assertEqual("2119", self.mapper.aind_protocol)

    def test_map_surgery_date(self):
        """Test surgery date mapping"""
        self.assertIsNotNone(self.mapper.aind_date_of_surgery)
        self.assertEqual(str(self.mapper.aind_date_of_surgery), "2022-01-03")

    def test_map_animal_weights(self):
        """Test animal weight mappings"""
        self.assertEqual(self.mapper.aind_weight_before_surger, Decimal("25.2"))
        self.assertEqual(self.mapper.aind_weight_after_surgery, Decimal("28.2"))

    def test_map_workstation_id(self):
        """Test workstation ID mapping"""
        self.assertEqual(self.mapper.aind_hp_work_station, "SWS 4")

    def test_map_bregma_lambda_distance(self):
        """Test bregma-lambda distance returns absolute value"""
        self.assertEqual(self.mapper.aind_breg2_lamb, Decimal("4.5"))


class TestNSB2023HeadframeMapping(TestCase):
    """Tests headframe procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.headframe_data = {
            "FileSystemObjectType": 0,
            "Id": 2,
            "Headpost": "Visual Ctx",
            "HeadpostType": "Mesoscope",
            "Headpost_x0020_Perform_x0020_Dur": "Initial Surgery",
            "Procedure": "Stereotaxic Injection (with Headpost)",
            "Date_x0020_of_x0020_Surgery": "2022-01-03",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
        }
        cls.nsb_model = NSB2023List.model_validate(cls.headframe_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_from_hp_and_hp_type(self):
        """Tests mapping of headpost information with all combinations"""
        # Test case 1: Visual Ctx with Mesoscope
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            HeadPost.VISUAL_CTX, HeadPostType.MESOSCOPE
        )
        self.assertEqual(hp_info.headframe_type, "Visual Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-10")
        self.assertEqual(hp_info.well_type, "Mesoscope")
        self.assertEqual(hp_info.well_part_number, "0160-200-20")
        self.assertIsNone(hp_info.headframe_material)
        
        # Test case 2: WHC NP with WHC NP well
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            HeadPost.WHC_NP, HeadPostType.WHC_NP
        )
        self.assertEqual(hp_info.headframe_type, "WHC NP")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-42")
        self.assertEqual(hp_info.well_type, "WHC NP")
        self.assertEqual(hp_info.well_part_number, "0160-055-08")
        
        # Test case 3: WHC 2P with WHC 2P well
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            HeadPost.WHC_2P, HeadPostType.WHC_2P
        )
        self.assertEqual(hp_info.headframe_type, "WHC 2P")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-45")
        self.assertEqual(hp_info.well_type, "WHC 2P")
        self.assertEqual(hp_info.well_part_number, "0160-200-62")
        
        # Test case 4: Frontal Ctx with CAM
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            HeadPost.FRONTAL_CTX, HeadPostType.CAM
        )
        self.assertEqual(hp_info.headframe_type, "Frontal Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-46")
        self.assertEqual(hp_info.well_type, "Scientifica (CAM)")
        self.assertEqual(hp_info.well_part_number, "Rev A")
        
        # Test case 5: Motor Ctx with Neuropixel
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            HeadPost.MOTOR_CTX, HeadPostType.NEUROPIXEL
        )
        self.assertEqual(hp_info.headframe_type, "Motor Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-51")
        self.assertEqual(hp_info.well_type, "Neuropixel")
        self.assertEqual(hp_info.well_part_number, "0160-200-36")
        
        # Test case 6: DHC with DHC Well (special case with Titanium material)
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            HeadPost.DHC, HeadPostType.DHC_WELL
        )
        self.assertEqual(hp_info.headframe_type, "DHC")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-57")
        self.assertEqual(hp_info.headframe_material, HeadframeMaterial.TITANIUM)
        self.assertEqual(hp_info.well_type, "DHC well")
        self.assertEqual(hp_info.well_part_number, "0160-075-01")
        
        # Test case 7: Both None
        hp_info = HeadPostInfo.from_hp_and_hp_type(None, None)
        self.assertIsNone(hp_info.headframe_type)
        self.assertIsNone(hp_info.headframe_part_number)
        self.assertIsNone(hp_info.well_type)
        self.assertIsNone(hp_info.well_part_number)
        self.assertIsNone(hp_info.headframe_material)
        
        # Test case 8: Only headpost provided, no well type
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            HeadPost.VISUAL_CTX, None
        )
        self.assertEqual(hp_info.headframe_type, "Visual Ctx")
        self.assertEqual(hp_info.headframe_part_number, "0160-100-10")
        self.assertIsNone(hp_info.well_type)
        self.assertIsNone(hp_info.well_part_number)
        
        # Test case 9: Only well type provided, no headpost
        hp_info = HeadPostInfo.from_hp_and_hp_type(
            None, HeadPostType.MESOSCOPE
        )
        self.assertIsNone(hp_info.headframe_type)
        self.assertIsNone(hp_info.headframe_part_number)
        self.assertEqual(hp_info.well_type, "Mesoscope")
        self.assertEqual(hp_info.well_part_number, "0160-200-20")

    def test_map_headframe_type(self):
        """Test Visual Ctx headframe type mapping"""
        self.assertEqual(self.mapper.aind_headpost, HeadPost.VISUAL_CTX)

    def test_map_headframe_well_type(self):
        """Test headframe well type mapping"""
        self.assertEqual(self.mapper.aind_headpost_type, HeadPostType.MESOSCOPE)

    def test_map_headframe_during(self):
        """Test headframe during (initial/followup) mapping"""
        self.assertEqual(self.mapper.aind_headpost_perform_dur, During.INITIAL)

    def test_has_hp_procedure(self):
        """Test detection of headpost procedure"""
        self.assertTrue(self.mapper.has_hp_procedure())

    def test_map_headframe_procedure(self):
        """Test creation of Headframe procedure"""
        surgeries = self.mapper.get_surgeries()
        
        # Find surgery with headframe
        headframe_surgery = next(
            (s for s in surgeries 
             if any(isinstance(p, Headframe) for p in s.procedures)),
            None
        )
        
        self.assertIsNotNone(headframe_surgery)
        headframe = next(
            p for p in headframe_surgery.procedures if isinstance(p, Headframe)
        )
        self.assertEqual(headframe.object_type, "Headframe")
        self.assertEqual(headframe.headframe_type, "Visual Ctx")
        self.assertEqual(headframe.well_type, "Mesoscope")

    def test_map_different_headframe_types(self):
        """Test various headframe type mappings"""
        test_cases = [
            ("Frontal Ctx", HeadPost.FRONTAL_CTX),
            ("Motor Ctx", HeadPost.MOTOR_CTX),
            ("WHC NP", HeadPost.WHC_NP),
            ("WHC 2P", HeadPost.WHC_2P),
        ]
        
        for headpost_value, expected_enum in test_cases:
            with self.subTest(headpost=headpost_value):
                test_data = deepcopy(self.headframe_data)
                test_data["Headpost"] = headpost_value
                
                nsb_model = NSB2023List.model_validate(test_data)
                mapper = MappedNSBList(nsb=nsb_model)
                
                self.assertEqual(mapper.aind_headpost, expected_enum)


class TestNSB2023CraniotomyMapping(TestCase):
    """Tests craniotomy procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.craniotomy_data = {
            "FileSystemObjectType": 0,
            "Id": 3,
            "CraniotomyType": "5mm",
            "Craniotomy_x0020_perform_x0020_d": "Initial Surgery",
            "Procedure": "Sx-01 Visual Ctx 2P",
            "Headpost": "Visual Ctx",
            "Headpost_Type": "Mesoscope",
            "Date_x0020_of_x0020_Surgery": "2022-01-03",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
        }
        cls.craniotomy_data_3mm = {
            "FileSystemObjectType": 0,
            "Id": 3,
            "CraniotomyType": "5mm",
            "Craniotomy_x0020_perform_x0020_d": "Initial Surgery",
            "Procedure": "Sx-01 Visual Ctx 2P",
            "Headpost": "Visual Ctx",
            "Headpost_Type": "Mesoscope",
            "Date_x0020_of_x0020_Surgery": "2022-01-03",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
        }
        cls.nsb_model = NSB2023List.model_validate(cls.craniotomy_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_craniotomy_type_5mm(self):
        """Test 5mm craniotomy type mapping"""
        self.assertEqual(self.mapper.aind_craniotomy_type, CraniotomyType.CIRCLE)

    def test_map_craniotomy_size(self):
        """Test craniotomy size mapping"""
        self.assertEqual(self.mapper.aind_craniotomy_size, 5.0)

    def test_map_craniotomy_coordinates(self):
        """Test craniotomy coordinate system mapping"""
        coord_sys = self.mapper.aind_craniotomy_coordinates_reference
        self.assertIsNotNone(coord_sys)
        self.assertEqual(coord_sys.name, "LAMBDA_ARI")

    def test_map_craniotomy_position(self):
        """Test craniotomy position mapping"""
        position = self.mapper.aind_craniotomy_coordinates
        self.assertIsNotNone(position)
        self.assertEqual(position.translation, [1.3, -2.8, 0])

    def test_has_cran_procedure(self):
        """Test detection of craniotomy procedure"""
        self.assertTrue(self.mapper.has_cran_procedure())

    def test_map_craniotomy_procedure(self):
        """Test creation of Craniotomy procedure"""
        surgeries = self.mapper.get_surgeries()
        
        craniotomy_surgery = next(
            (s for s in surgeries 
             if any(isinstance(p, Craniotomy) for p in s.procedures)),
            None
        )
        
        self.assertIsNotNone(craniotomy_surgery)
        craniotomy = next(
            p for p in craniotomy_surgery.procedures if isinstance(p, Craniotomy)
        )
        self.assertEqual(craniotomy.craniotomy_type, CraniotomyType.CIRCLE)
        self.assertEqual(craniotomy.size, 5.0)


class TestNSB2023InjectionMapping(TestCase):
    """Tests brain injection procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.injection_data = {
            "FileSystemObjectType": 0,
            "Id": 4,
            "Burr_x0020_hole_x0020_2": "Injection",
            "ML2ndInj": 3.0,
            "AP2ndInj": -2.45,
            "DV2ndInj": 3.1,
            "Hemisphere2ndInj": "Right",
            "Inj2Type": "Nanoject (Pressure)",
            "inj2volperdepth": 500.2,
            "Burr2_x0020_Perform_x0020_During": "Initial Surgery",
            "Inj2Angle_v2": 10.0,
            "Date_x0020_of_x0020_Surgery": "2022-01-03",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
            "Burr_x0020_2_x0020_Intended_x002": ["FRP - Frontal pole cerebral cortex"]


        }
        cls.nsb_model = NSB2023List.model_validate(cls.injection_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_burr_hole_procedure_type(self):
        """Test burr hole procedure type mapping"""
        self.assertEqual(self.mapper.aind_burr_hole_2, BurrHoleProcedure.INJECTION)

    def test_map_injection_coordinates(self):
        """Test injection coordinate mapping"""
        self.assertEqual(self.mapper.aind_ml2nd_inj, Decimal("3.0"))
        self.assertEqual(self.mapper.aind_ap2nd_inj, Decimal("-2.45"))
        self.assertEqual(self.mapper.aind_dv2nd_inj, Decimal("3.1"))

    def test_map_injection_type_nanoject(self):
        """Test Nanoject injection type mapping"""
        self.assertEqual(self.mapper.aind_inj2_type, InjectionType.NANOJECT)

    def test_map_injection_volume(self):
        """Test injection volume mapping"""
        self.assertEqual(self.mapper.aind_inj2volperdepth, Decimal("500.2"))

    def test_map_injection_hemisphere(self):
        """Test injection hemisphere mapping"""
        hemisphere = self.mapper.aind_hemisphere2nd_inj
        self.assertIsNotNone(hemisphere)
        self.assertEqual(hemisphere.value, "Right")

    def test_map_burr_hole_info(self):
        """Test burr hole info compilation"""
        burr_info = self.mapper.burr_hole_info(2)
        self.assertIsNotNone(burr_info)
        self.assertEqual(burr_info.coordinate_ml, Decimal("3.0"))
        self.assertEqual(burr_info.coordinate_ap, Decimal("-2.45"))
        self.assertIsInstance(burr_info.targeted_structure[0], BrainStructureModel)
        self.assertEqual(burr_info.targeted_structure[0].name, "Frontal pole, cerebral cortex")
        self.assertIn(Decimal("3.1"), burr_info.coordinate_depth)

    def test_map_burr_hole_during(self):
        """Test burr hole during mapping"""
        self.assertEqual(self.mapper.aind_burr2_perform_during, During.INITIAL)

    def test_map_iontophoresis_injection(self):
        """Test iontophoresis injection type"""
        test_data = deepcopy(self.injection_data)
        test_data["Inj2Type"] = "Iontophoresis"
        test_data["Inj2Current"] = "5 uA"
        test_data["Inj2IontoTime"] = "10 min"
        
        nsb_model = NSB2023List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        self.assertEqual(mapper.aind_inj2_type, InjectionType.IONTOPHORESIS)
        self.assertEqual(mapper.aind_inj2_current, Decimal("5"))
        self.assertEqual(mapper.aind_inj2_ionto_time, Decimal("10"))

    def test_map_targeted_structures(self):
        test_data = {
                "Burr_x0020_1_x0020_Intended_x002": ["INVALID"],
                "Burr_x0020_2_x0020_Intended_x002": ["FRP - Frontal pole cerebral cortex"],
                "Burr_x0020_3_x0020_Intended_x002": [None],
                "Burr_x0020_4_x0020_Intended_x002": ["PL - Prelimbic area"],
                "Burr_x0020_5_x0020_Intended_x002": ["DG - Dentate gyrus"],
                "Burr_x0020_6_x0020_Intended_x002": ["CA1 - Field CA1", "CA2 - Field CA2"]
        }
        nsb_model = NSB2023List.model_construct(**test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        self.assertEqual(mapper.aind_burr_1_intended, [])
        self.assertEqual(mapper.aind_burr_2_intended[0].name, "Frontal pole, cerebral cortex")
        self.assertEqual(mapper.aind_burr_3_intended, [])
        self.assertIsNotNone(mapper.aind_burr_4_intended[0])
        self.assertIsNotNone(mapper.aind_burr_5_intended[0])
        self.assertEqual(len(mapper.aind_burr_6_intended), 2)



class TestNSB2023FiberImplantMapping(TestCase):
    """Tests fiber implant/probe implant mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.fiber_data = {
            "FileSystemObjectType": 0,
            "Id": 5,
            "Burr_x0020_hole_x0020_1": "Fiber Implant",
            "FiberImplant2DV": -2.0,
            "Fiber_x0020_Implant2_x0020_Lengt": "4.5 mm",
            "Burr_x0020_2_x0020_Fiber_x0020_T": "Standard (Provided by NSB)",
            "Burr1_x0020_Perform_x0020_During": "Initial Surgery",
            "Date_x0020_of_x0020_Surgery": "2022-01-03",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
        }
        cls.nsb_model = NSB2023List.model_validate(cls.fiber_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_fiber_implant_procedure_type(self):
        """Test fiber implant procedure type detection"""
        self.assertEqual(
            self.mapper.aind_burr_hole_1, 
            BurrHoleProcedure.FIBER_IMPLANT
        )

    def test_map_fiber_implant_depth(self):
        """Test fiber implant depth mapping"""
        self.assertEqual(self.mapper.aind_fiber_implant2_dv, Decimal("-2.0"))

    def test_map_fiber_implant_length(self):
        """Test fiber implant length mapping"""
        self.assertEqual(self.mapper.aind_fiber_implant2_lengt, Decimal("4.5"))

    def test_map_fiber_type_standard(self):
        """Test standard fiber type mapping"""
        self.assertEqual(self.mapper.aind_burr_2_fiber_t, FiberType.STANDARD)

    def test_map_fiber_type_custom(self):
        """Test custom fiber type mapping"""
        test_data = deepcopy(self.fiber_data)
        test_data["Burr_x0020_2_x0020_Fiber_x0020_T"] = "Custom"
        test_data["LongRequestorComments"] = "Custom fiber details"
        
        nsb_model = NSB2023List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        self.assertEqual(mapper.aind_burr_2_fiber_t, FiberType.CUSTOM)
        self.assertEqual(
            mapper.aind_long_requestor_comments, "Custom fiber details"
        )

class TestNSB2023SpinalInjectionMapping(TestCase):
    """Tests spinal injection procedure mapping"""

    def test_map_spinal_location_c1_c2(self):
        """Test spinal location mapping for C1-C2"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 6,
            "Burr_x0020_1_x0020_Spinal_x0020_": "Between C1-C2",
        }
        nsb_model = NSB2023List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        self.assertEqual(mapper.aind_burr_1_spinal_location, Origin.BETWEEN_C1_C2)

    def test_map_spinal_coordinate_system_name(self):
        """Test spinal coordinate system name generation"""
        c1c2_name = MappedNSBList._get_spinal_coordinate_system_name(
            Origin.BETWEEN_C1_C2
        )
        self.assertEqual(c1c2_name, "C1C2_ARID")

        none_name = MappedNSBList._get_spinal_coordinate_system_name(None)
        self.assertEqual(none_name, "Spinal_ARID")
        
        tip_name = MappedNSBList._get_spinal_coordinate_system_name(Origin.TIP)
        self.assertEqual(tip_name, "Spinal_ARID")

    def test_map_various_spinal_locations(self):
        """Test different spinal location mappings"""
        test_cases = [
            ("Between C2-C3", Origin.BETWEEN_C2_C3, "C2C3_ARID"),
            ("Between C3-C4", Origin.BETWEEN_C3_C4, "C3C4_ARID"),
            ("Between T1-T2", Origin.BETWEEN_T1_T2, "T1T2_ARID"),
        ]
        
        for location_str, expected_origin, expected_coord_name in test_cases:
            with self.subTest(location=location_str):
                nsb_data = {
                    "FileSystemObjectType": 0,
                    "Id": 1,
                    "Burr_x0020_1_x0020_Spinal_x0020_": location_str,
                }
                nsb_model = NSB2023List.model_validate(nsb_data)
                mapper = MappedNSBList(nsb=nsb_model)
                
                self.assertEqual(
                    mapper.aind_burr_1_spinal_location, 
                    expected_origin
                )
                coord_name = mapper._get_spinal_coordinate_system_name(
                    expected_origin
                )
                self.assertEqual(coord_name, expected_coord_name)

    def test_determine_coordinate_system_spinal_injection(self):
        """Test coordinate system determination with T1-T2 spinal injection"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 3,
            "Burr_x0020_hole_x0020_2": "Spinal Injection",
            "Burr_x0020_2_x0020_Spinal_x0020_": "Between T1-T2",
            "Burr2_x0020_Perform_x0020_During": "Follow up Surgery",
        }
        nsb_model = NSB2023List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)
        
        coord_sys = mapper.determine_surgery_coordinate_system(During.FOLLOW_UP)
        self.assertIsNotNone(coord_sys)
        self.assertEqual(coord_sys.name, "T1T2_ARID")
        self.assertEqual(coord_sys.origin, Origin.BETWEEN_T1_T2)


class TestNSB2023SurgeryIntegration(TestCase):
    """Tests complete Surgery object creation"""

    @classmethod
    def setUpClass(cls):
        """Create comprehensive test data"""
        # Test data for headframe/craniotomy procedures (INITIAL)
        cls.hp_cran_surgery_data = {
            "FileSystemObjectType": 0,
            "Id": 7,
            "Date_x0020_of_x0020_Surgery": "2022-01-03",
            "Weight_x0020_before_x0020_Surger": 25.2,
            "Weight_x0020_after_x0020_Surgery": 28.2,
            "HpWorkStation": "SWS 4",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
            "Headpost": "Visual Ctx",
            "HeadpostType": "Mesoscope",
            "Headpost_x0020_Perform_x0020_Dur": "Initial Surgery",
            "CraniotomyType": "5mm",
            "Craniotomy_x0020_Perform_x0020_D": "Initial Surgery",
            "Procedure": "Sx-01 Visual Ctx 2P",
            "Test1LookupId": 2846,
            "Breg2Lamb": 4.5,
            "Iso_x0020_On": 1.5,
            "HPIsoLevel": 2.0,
            "HPRecovery": 25,
        }
        
        # Test data for fiber implant procedures (INITIAL with HP fields)
        cls.fiber_implant_surgery_data = {
            "FileSystemObjectType": 0,
            "Id": 10,
            "Date_x0020_of_x0020_Surgery": "2022-03-15",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
            "Test1LookupId": 2846,
            "Burr_x0020_hole_x0020_1": "Fiber Implant",
            "Virus_x0020_M_x002f_L": 2.0,
            "Virus_x0020_A_x002f_P": 3.0,
            "Virus_x0020_D_x002f_V": 4.0,
            "Burr1_x0020_Perform_x0020_During": "Initial Surgery",
            "Burr_x0020_1_x0020_Fiber_x0020_T": "Standard (Provided by NSB)",
            "Fiber_x0020_Implant1_x0020_Lengt": "2.0 mm",
            "Burr_x0020_hole_x0020_2": "Fiber Implant",
            "ML2ndInj": 1.5,
            "AP2ndInj": 3.0,
            "DV2ndInj": 3.5,
            "Burr2_x0020_Perform_x0020_During": "Initial Surgery",
            "Burr_x0020_2_x0020_Fiber_x0020_T": "Standard (Provided by NSB)",
            "Fiber_x0020_Implant2_x0020_Lengt": "5.0 mm",
            # For INITIAL surgery, use HP fields with correct backend names:
            "Iso_x0020_On": 1.5,  # Backend field name (not just "ISOon")
            "HPIsoLevel": 1.8,
            "HPRecovery": 30,
        }
        
        # Test data for follow-up fiber implant procedures
        cls.fiber_followup_surgery_data = {
            "FileSystemObjectType": 0,
            "Id": 11,
            "Date_x0020_of_x0020_Surgery": "2022-03-01",
            "Date1stInjection": "2022-03-15",
            "IACUC_x0020_Protocol_x0020__x002": "2103",
            "Test1LookupId": 2846,
            "test_x0020_1st_x0020_round_x0020_LookupId": 2847,
            "Burr_x0020_hole_x0020_1": "Fiber Implant",
            "Virus_x0020_M_x002f_L": 2.0,
            "Virus_x0020_A_x002f_P": 3.0,
            "Virus_x0020_D_x002f_V": 4.0,
            "Burr1_x0020_Perform_x0020_During": "Follow up Surgery",
            "Burr_x0020_1_x0020_Fiber_x0020_T": "Standard (Provided by NSB)",
            "Fiber_x0020_Implant1_x0020_Lengt": "2.0 mm",
            # For FOLLOW-UP surgery, use First* fields with correct backend names:
            "FirstInjectionIsoDuration": 1.5,  # Backend field name
            "Round1InjIsolevel": 2.5,  # Backend field name
            "FirstInjRecovery": 35,  # Backend field name
            "FirstInjectionWeightBefor": 26.5,
            "FirstInjectionWeightAfter": 29.0,
            "WorkStation1stInjection": "SWS 5",
        }
        
        # Create mappers for all datasets
        cls.hp_cran_model = NSB2023List.model_validate(cls.hp_cran_surgery_data)
        cls.hp_cran_mapper = MappedNSBList(nsb=cls.hp_cran_model)
        cls.hp_cran_surgeries = cls.hp_cran_mapper.get_surgeries()
        
        cls.fiber_model = NSB2023List.model_validate(cls.fiber_implant_surgery_data)
        cls.fiber_mapper = MappedNSBList(nsb=cls.fiber_model)
        cls.fiber_surgeries = cls.fiber_mapper.get_surgeries()
        
        cls.fiber_followup_model = NSB2023List.model_validate(cls.fiber_followup_surgery_data)
        cls.fiber_followup_mapper = MappedNSBList(nsb=cls.fiber_followup_model)
        cls.fiber_followup_surgeries = cls.fiber_followup_mapper.get_surgeries()

    def test_get_surgeries_basic_structure_hp_cran(self):
        """Test basic surgery creation for headframe/craniotomy"""
        self.assertIsInstance(self.hp_cran_surgeries, list)
        self.assertGreater(len(self.hp_cran_surgeries), 0)
        
        for surgery in self.hp_cran_surgeries:
            self.assertIsInstance(surgery, Surgery)
            self.assertIsNotNone(surgery.experimenters)
            self.assertGreater(len(surgery.experimenters), 0)

    def test_get_surgeries_basic_structure_fiber(self):
        """Test basic surgery creation for fiber implants"""
        self.assertIsInstance(self.fiber_surgeries, list)
        self.assertGreater(len(self.fiber_surgeries), 0)
        
        for surgery in self.fiber_surgeries:
            self.assertIsInstance(surgery, Surgery)
            self.assertIsNotNone(surgery.experimenters)
            self.assertGreater(len(surgery.experimenters), 0)

    def test_get_surgeries_with_multiple_procedures(self):
        """Test surgery with headframe and craniotomy procedures"""
        combined_surgery = next(
            (s for s in self.hp_cran_surgeries 
             if any(isinstance(p, Headframe) for p in s.procedures)
             and any(isinstance(p, Craniotomy) for p in s.procedures)),
            None
        )
        self.assertIsNotNone(combined_surgery)
        self.assertIsNotNone(combined_surgery.anaesthesia)
        self.assertEqual(
            combined_surgery.anaesthesia.anaesthetic_type, 
            "isoflurane"
        )

    def test_surgery_during_info_initial_hp_cran(self):
        """Test surgery during info for initial surgery with headframe/craniotomy"""
        during_info = self.hp_cran_mapper.surgery_during_info(During.INITIAL)
        
        self.assertIsNotNone(during_info.start_date)
        self.assertEqual(str(during_info.start_date), "2022-01-03")
        
        self.assertIsNotNone(during_info.workstation_id)
        self.assertEqual(during_info.workstation_id, "SWS 4")
        self.assertEqual(during_info.anaesthetic_level, 2.0)
        self.assertEqual(during_info.recovery_time, 25.0)
        self.assertEqual(during_info.anaesthetic_duration_in_minutes, 90)

    def test_surgery_during_info_initial_fiber(self):
        """Test surgery during info for initial surgery with fiber implants"""
        during_info = self.fiber_mapper.surgery_during_info(During.INITIAL)
        
        self.assertIsNotNone(during_info.start_date)
        self.assertEqual(str(during_info.start_date), "2022-03-15")
        self.assertEqual(during_info.anaesthetic_duration_in_minutes, 90)
        self.assertEqual(during_info.recovery_time, 30.0)
        self.assertEqual(during_info.anaesthetic_level, Decimal('1.8'))

    def test_surgery_during_info_followup_fiber(self):
        """Test surgery during info for follow-up surgery with fiber implants"""
        during_info = self.fiber_followup_mapper.surgery_during_info(During.FOLLOW_UP)
        
        self.assertIsNotNone(during_info.start_date)
        self.assertEqual(str(during_info.start_date), "2022-03-15")
        self.assertEqual(during_info.anaesthetic_duration_in_minutes, 90)
        self.assertEqual(during_info.recovery_time, 35.0)
        self.assertEqual(during_info.anaesthetic_level, 2.5)
        self.assertEqual(during_info.workstation_id, "SWS 5")
        self.assertEqual(during_info.weight_prior, Decimal("26.5"))
        self.assertEqual(during_info.weight_post, Decimal("29.0"))

    def test_determine_surgery_coordinate_system_hp_cran(self):
        """Test coordinate system determination for headframe/craniotomy"""
        coord_sys = self.hp_cran_mapper.determine_surgery_coordinate_system(During.INITIAL)
        self.assertIsNotNone(coord_sys)
        self.assertIn("LAMBDA", coord_sys.name)

    def test_determine_surgery_coordinate_system_fiber(self):
        """Test coordinate system determination for fiber implants"""
        coord_sys = self.fiber_mapper.determine_surgery_coordinate_system(During.INITIAL)
        self.assertIsNotNone(coord_sys)
        # Should be BREGMA_ARID since fiber implants have depth coordinates
        self.assertEqual(coord_sys, CoordinateSystemLibrary.BREGMA_ARID)

    def test_map_measured_coordinates(self):
        """Test measured coordinates mapping"""
        coord_sys = CoordinateSystem(
            name="LAMBDA_ARI",
            origin=Origin.LAMBDA,
            axis_unit=SizeUnit.MM,
            axes=[
                Axis(name=AxisName.AP, direction=Direction.PA),
                Axis(name=AxisName.ML, direction=Direction.LR),
                Axis(name=AxisName.SI, direction=Direction.SI),
            ],
        )
        measured = MappedNSBList.map_measured_coordinates(
            Decimal("4.5"), coord_sys
        )
        self.assertIsNotNone(measured)
        self.assertIn(Origin.BREGMA, measured)

    def test_fiber_probe_integration_full_surgery(self):
        """Test full fiber probe workflow in surgery creation"""
        self.assertEqual(len(self.fiber_surgeries), 1)
        surgery = self.fiber_surgeries[0]
        
        probe_implants = [
            p for p in surgery.procedures 
            if isinstance(p, ProbeImplant)
        ]
        self.assertEqual(len(probe_implants), 2)
        
        probe_names = [
            p.implanted_device.name for p in probe_implants
        ]
        self.assertIn("Fiber_0", probe_names)
        self.assertIn("Fiber_1", probe_names)
        
        # Verify fiber probes are correctly configured
        for probe_implant in probe_implants:
            fiber_probe = probe_implant.implanted_device
            self.assertIsInstance(fiber_probe, FiberProbe)
            self.assertIsNotNone(fiber_probe.name)
            self.assertIsNotNone(fiber_probe.total_length)


class TestNSB2023CoordinateMapping(TestCase):
    """Tests coordinate and transform mapping"""

    def test_map_burr_hole_transforms_with_depth(self):
        """Test burr hole transforms with depth"""
        transforms = MappedNSBList._map_burr_hole_transforms(
            angle=Decimal("10"),
            ml=Decimal("2.0"),
            ap=Decimal("1.5"),
            depth=[Decimal("3.0")],
            surgery_coordinate_system=CoordinateSystemLibrary.BREGMA_ARID,
        )
        self.assertIsInstance(transforms, list)
        self.assertGreater(len(transforms), 0)

    def test_map_burr_hole_transforms_without_depth(self):
        """Test burr hole transforms without depth"""
        transforms = MappedNSBList._map_burr_hole_transforms(
            angle=Decimal("10"),
            ml=Decimal("2.0"),
            ap=Decimal("1.5"),
            depth=None,
            surgery_coordinate_system=CoordinateSystemLibrary.BREGMA_ARI,
        )
        self.assertIsInstance(transforms, list)
        self.assertEqual(len(transforms), 1)

    def test_map_burr_hole_dv_list(self):
        """Test DV coordinate list mapping"""
        # All values present
        dv_list = MappedNSBList._map_burr_hole_dv(
            Decimal("3.0"), Decimal("4.0"), Decimal("5.0")
        )
        self.assertEqual(
            dv_list, 
            [Decimal("3.0"), Decimal("4.0"), Decimal("5.0")]
        )
        
        # Some None values
        dv_list_partial = MappedNSBList._map_burr_hole_dv(
            Decimal("3.0"), Decimal("4.0"), None
        )
        self.assertEqual(dv_list_partial, [Decimal("3.0"), Decimal("4.0")])
        
        # All None
        dv_list_none = MappedNSBList._map_burr_hole_dv(None, None, None)
        self.assertIsNone(dv_list_none)


class TestNSB2023StringParsers(TestCase):
    """Tests text field parsers in NSB2023Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Create blank mapper for parser testing"""
        cls.blank_model = MappedNSBList(
            nsb=NSB2023List.model_validate({
                "FileSystemObjectType": 0, 
                "Id": 0
            })
        )

    def test_parse_float_to_decimal(self):
        """Test float to decimal conversion"""
        result = MappedNSBList._map_float_to_decimal(3.14)
        self.assertEqual(result, Decimal("3.14"))
        
        result_int = MappedNSBList._map_float_to_decimal(5.0)
        self.assertEqual(result_int, Decimal("5.0"))
        
        result_none = MappedNSBList._map_float_to_decimal(None)
        self.assertIsNone(result_none)

    def test_parse_basic_decimal_str(self):
        """Test basic decimal string parsing"""
        test_cases = [
            ("3.14", Decimal("3.14")),
            ("10", Decimal("10")),
            ("0.001", Decimal("0.001")),
            (None, None),
            ("invalid", None),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.blank_model._parse_basic_decimal_str(input_str)
                self.assertEqual(result, expected)

    def test_parse_current_str(self):
        """Test current string parsing"""
        test_cases = [
            ("5 uA", Decimal("5")),
            ("10 uAmp", Decimal("10")),
            ("3.5 ua", Decimal("3.5")),
            (None, None),
            ("invalid", None),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.blank_model._parse_current_str(input_str)
                self.assertEqual(result, expected)

    def test_parse_length_of_time_str(self):
        """Test length of time string parsing"""
        test_cases = [
            ("10 min", Decimal("10")),
            ("5 minutes", Decimal("5")),
            ("2.5 m", Decimal("2.5")),
            (None, None),
            ("invalid", None),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.blank_model._parse_length_of_time_str(input_str)
                self.assertEqual(result, expected)

    def test_parse_fiber_length_mm_str(self):
        """Test fiber length string parsing"""
        result = self.blank_model._parse_fiber_length_mm_str("6.5 mm")
        self.assertEqual(result, Decimal("6.5"))
        
        result_other = self.blank_model._parse_fiber_length_mm_str("4.2 mm")
        self.assertEqual(result_other, Decimal("4.2"))

    def test_is_titer(self):
        """Test titer detection"""
        self.assertTrue(self.blank_model._is_titer("1.5e12"))
        self.assertTrue(self.blank_model._is_titer("3.2E10"))
        self.assertTrue(self.blank_model._is_titer("5e+8"))
        self.assertFalse(self.blank_model._is_titer("0.5 mg/ml"))
        self.assertFalse(self.blank_model._is_titer("regular text"))

    def test_is_concentration(self):
        """Test concentration detection"""
        self.assertTrue(self.blank_model._is_concentration("0.5 mg/ml"))
        self.assertTrue(self.blank_model._is_concentration("2.5 mg/mL"))
        self.assertTrue(self.blank_model._is_concentration("10 mg/ml"))
        self.assertFalse(self.blank_model._is_concentration("1.5e12"))
        self.assertFalse(self.blank_model._is_concentration("regular text"))


if __name__ == "__main__":
    unittest_main()
