"""Tests NSB 2019 data model is parsed correctly"""

from copy import deepcopy
from decimal import Decimal
from unittest import TestCase
from unittest import main as unittest_main
from aind_data_schema.components.devices import FiberProbe
from aind_data_schema.components.configs import ProbeConfig
from aind_metadata_service_server.mappers.nsb2019 import InjectionType
from aind_data_schema.components.coordinates import (
    CoordinateSystemLibrary,
    Origin,
)
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema.components.surgery_procedures import (
    BrainInjection,
    Craniotomy,
    CraniotomyType,
    Headframe,
    ProbeImplant,
)
from aind_data_schema.components.injection_procedures import (
    InjectionProfile,
)
from aind_data_schema_models.units import (
    CurrentUnit,
    TimeUnit,
    VolumeUnit,
)
from aind_data_schema_models.coordinates import AnatomicalRelative
from aind_sharepoint_service_async_client.models.nsb2019_list import (
    NSB2019List,
)

from aind_metadata_service_server.mappers.nsb2019 import MappedNSBList


class TestNSB2019BasicMapping(TestCase):
    """Tests basic NSB2019 mapping functionality"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.basic_nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 5554,
            "Date_x0020_of_x0020_Surgery": "2022-12-06T08:00:00Z",
            "Weight_x0020_before_x0020_Surger": "19.1",
            "Weight_x0020_after_x0020_Surgery": "19.2",
            "HpWorkStation": "SWS 3",
            "IACUC_x0020_Protocol_x0020__x002": "2115",
            "Breg2Lamb": "4",
            "AuthorId": 187,
            "Date2ndInjection": None,
        }
        cls.nsb_model = NSB2019List.model_validate(cls.basic_nsb_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_experimenter_full_name(self):
        """Test experimenter full name mapping"""
        self.assertEqual(self.mapper.aind_experimenter_full_name, "NSB-187")
        nsb_model_no_author = NSB2019List.model_validate(
            {"FileSystemObjectType": 0, "Id": 1}
        )
        mapper_no_author = MappedNSBList(nsb=nsb_model_no_author)
        self.assertEqual(mapper_no_author.aind_experimenter_full_name, "NSB")

    def test_map_anaesthetic_type(self):
        """Test anaesthetic type is always isoflurane"""
        self.assertEqual(self.mapper.aind_anaesthetic_type, "isoflurane")

    def test_map_iacuc_protocol(self):
        """Test IACUC protocol mapping"""
        self.assertEqual(self.mapper.aind_iacuc_protocol, "2115")

    def test_map_surgery_date(self):
        """Test surgery date mapping"""
        self.assertIsNotNone(self.mapper.aind_date_of_surgery)
        self.assertEqual(str(self.mapper.aind_date_of_surgery), "2022-12-06")
        self.assertIsNone(self.mapper.aind_date2nd_injection)

    def test_map_animal_weights(self):
        """Test animal weight mappings"""
        self.assertEqual(
            self.mapper.aind_weight_before_surger, Decimal("19.1")
        )
        self.assertEqual(
            self.mapper.aind_weight_after_surgery, Decimal("19.2")
        )

    def test_map_workstation_id(self):
        """Test workstation ID mapping"""
        self.assertEqual(self.mapper.aind_hp_work_station, "SWS 3")

    def test_map_bregma_lambda_distance(self):
        """Test bregma-lambda distance returns absolute value"""
        self.assertEqual(self.mapper.aind_breg2_lamb, Decimal("4"))

        # Test with negative value
        test_data = deepcopy(self.basic_nsb_data)
        test_data["Breg2Lamb"] = "-4.5"
        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        self.assertEqual(mapper.aind_breg2_lamb, Decimal("4.5"))


class TestNSB2019HeadframeMapping(TestCase):
    """Tests headframe procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.headframe_data = {
            "FileSystemObjectType": 0,
            "Id": 5554,
            "HeadpostType": "AI Straight Headbar",
            "Procedure": "HP+Injection+Optic Fiber Implant",
            "Date_x0020_of_x0020_Surgery": "2022-12-06T08:00:00Z",
            "IACUC_x0020_Protocol_x0020__x002": "2115",
        }
        cls.nsb_model = NSB2019List.model_validate(cls.headframe_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_headframe_type(self):
        """Test AI Straight Headbar type mapping"""
        head_post_info = self.mapper.aind_headpost_type
        self.assertIsNotNone(head_post_info)
        self.assertEqual(head_post_info.headframe_type, "AI Straight Headbar")

    def test_has_head_frame_procedure(self):
        """Test detection of headframe procedure"""
        self.assertTrue(self.mapper.has_head_frame_procedure)

    def test_map_headframe_procedure(self):
        """Test creation of Headframe procedure"""
        headframe = self.mapper.get_head_frame_procedure()
        self.assertIsInstance(headframe, Headframe)
        self.assertEqual(headframe.object_type, "Headframe")
        self.assertEqual(headframe.headframe_type, "AI Straight Headbar")

    def test_map_different_headframe_types(self):
        """Test various headframe type mappings"""
        test_cases = [
            (
                "CAM-style headframe (0160-100-10 Rev A)",
                "CAM-style",
                "0160-100-10 Rev A",
            ),
            (
                "Neuropixel-style headframe (0160-100-10/0160-200-36)",
                "Neuropixel-style",
                "0160-100-10",
            ),
            (
                "Mesoscope-style well with NGC-style headframe (0160-200-20/0160-100-10)",
                "NGC-style",
                "0160-100-10",
            ),
            (
                "NGC-style headframe, no well (0160-100-10)",
                "NGC-style",
                "0160-100-10",
            ),
            ("WHC #42 with Neuropixel well and well cap", "WHC #42", "42"),
        ]

        for headpost_str, expected_type, expected_part in test_cases:
            with self.subTest(headpost=headpost_str):
                test_data = deepcopy(self.headframe_data)
                test_data["HeadpostType"] = headpost_str

                nsb_model = NSB2019List.model_validate(test_data)
                mapper = MappedNSBList(nsb=nsb_model)

                head_post = mapper.aind_headpost_type
                self.assertEqual(head_post.headframe_type, expected_type)
                if expected_part:
                    self.assertEqual(
                        head_post.headframe_part_number, expected_part
                    )


class TestNSB2019CraniotomyMapping(TestCase):
    """Tests craniotomy procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.craniotomy_data = {
            "FileSystemObjectType": 0,
            "Id": 5554,
            "CraniotomyType": "Visual Cortex 5mm",
            "Procedure": "HP+C Neuropixel style",
            "HpLoc": "Right",
            "HPDurotomy": "Yes",
            "Date_x0020_of_x0020_Surgery": "2022-12-06T08:00:00Z",
            "IACUC_x0020_Protocol_x0020__x002": "2115",
        }
        cls.nsb_model = NSB2019List.model_validate(cls.craniotomy_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_craniotomy_type_5mm(self):
        """Test 5mm craniotomy type mapping"""
        self.assertEqual(
            self.mapper.aind_craniotomy_type, CraniotomyType.CIRCLE
        )

    def test_map_craniotomy_size(self):
        """Test craniotomy size mapping"""
        self.assertEqual(self.mapper.aind_craniotomy_size, Decimal(5))

    def test_map_craniotomy_coordinates(self):
        """Test craniotomy coordinate system mapping"""
        coord_sys = self.mapper.aind_craniotomy_coordinates_reference
        self.assertEqual(coord_sys.name, "LAMBDA_ARI")

        test_data = deepcopy(self.craniotomy_data)
        test_data["CraniotomyType"] = "Frontal Window 3mm"
        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        no_coord_sys = mapper.aind_craniotomy_coordinates_reference
        self.assertIsNone(no_coord_sys)

    def test_map_craniotomy_position(self):
        """Test craniotomy position mapping"""
        self.assertEqual(self.mapper.aind_hp_loc, AnatomicalRelative.RIGHT)

    def test_map_dura_removed(self):
        """Test dura removed flag mapping"""
        self.assertTrue(self.mapper.aind_hp_durotomy)

    def test_has_craniotomy_procedure(self):
        """Test detection of craniotomy procedure"""
        self.assertTrue(self.mapper.has_craniotomy_procedure)

    def test_map_craniotomy_procedure(self):
        """Test creation of Craniotomy procedure"""
        craniotomy = self.mapper.get_craniotomy_procedure()
        self.assertIsInstance(craniotomy, Craniotomy)
        self.assertEqual(craniotomy.craniotomy_type, CraniotomyType.CIRCLE)
        self.assertEqual(craniotomy.size, Decimal(5))
        self.assertTrue(craniotomy.dura_removed)

    def test_map_3mm_craniotomy(self):
        """Test 3mm frontal craniotomy mapping"""
        test_data = deepcopy(self.craniotomy_data)
        test_data["CraniotomyType"] = "Frontal Window 3mm"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertEqual(mapper.aind_craniotomy_type, CraniotomyType.CIRCLE)
        self.assertEqual(mapper.aind_craniotomy_size, Decimal(3))


class TestNSB2019InjectionMapping(TestCase):
    """Tests brain injection procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.injection_data = {
            "FileSystemObjectType": 0,
            "Id": 5554,
            "Procedure": "Stereotaxic Injection",
            "Virus_x0020_A_x002f_P": "-1.6",
            "Virus_x0020_M_x002f_L": "-3.3",
            "Virus_x0020_D_x002f_V": "4.3",
            "Virus_x0020_Hemisphere": "Left",
            "Inj1Type": "Nanoject (Pressure)",
            "Inj1Vol": "400",
            "Inj1LenghtofTime": "5min",
            "Inj1Angle_v2": "0",
            "Date1stInjection": "2022-12-06T08:00:00Z",
            "FirstInjectionWeightBefor": "19.1",
            "FirstInjectionWeightAfter": "19.2",
            "FirstInjectionIsoDuration": "1 hour",
            "IACUC_x0020_Protocol_x0020__x002": "2115",
            "Breg2Lamb": "4",
        }
        cls.nsb_model = NSB2019List.model_validate(cls.injection_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_first_injection_properties(self):
        """Test first injection coordinate and property mapping"""
        # Coordinates
        self.assertEqual(self.mapper.aind_virus_a_p, Decimal("-1.6"))
        self.assertEqual(self.mapper.aind_virus_m_l, Decimal("-3.3"))
        self.assertEqual(self.mapper.aind_virus_d_v, Decimal("4.3"))
        self.assertEqual(
            self.mapper.aind_virus_hemisphere, AnatomicalRelative.LEFT
        )

        # Coordinate system
        self.assertEqual(
            self.mapper.aind_inj1_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARID,
        )

        # Injection parameters
        self.assertEqual(self.mapper.aind_inj1_type, InjectionType.NANOJECT)
        self.assertEqual(self.mapper.aind_inj1_vol[0], Decimal(400))
        self.assertEqual(self.mapper.aind_inj1_lenghtof_time, Decimal("5"))
        self.assertEqual(self.mapper.aind_inj1_angle_v2, Decimal("0"))

    def test_map_first_injection_dynamics(self):
        """Test first injection dynamics creation"""
        dynamics = self.mapper.aind_inj1_dynamics
        self.assertIsNotNone(dynamics)
        self.assertEqual(dynamics.profile, InjectionProfile.BOLUS)
        self.assertEqual(dynamics.volume[0], Decimal(400))
        self.assertEqual(dynamics.duration, Decimal("5"))

    def test_has_first_injection_procedure(self):
        """Test detection of first injection procedure"""
        self.assertTrue(self.mapper.has_injection_procedure)

    def test_map_first_injection_procedure(self):
        """Test creation of first BrainInjection procedure"""
        injection = self.mapper.get_first_injection_procedure()
        self.assertIsInstance(injection, BrainInjection)
        self.assertEqual(injection.object_type, "Brain injection")
        self.assertIsNotNone(injection.dynamics)

    def test_map_first_iontophoresis_injection(self):
        """Test iontophoresis injection type"""
        test_data = deepcopy(self.injection_data)
        test_data["Inj1Type"] = "Iontophoresis"
        test_data["Inj1Current"] = "5 uA"
        test_data["Inj1AlternatingTime"] = "7/7"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        dynamics = mapper.aind_inj1_dynamics

        self.assertEqual(mapper.aind_inj1_type, InjectionType.IONTOPHORESIS)
        self.assertEqual(mapper.aind_inj1_current, Decimal("5"))
        self.assertEqual(mapper.aind_inj1_alternating_time, "7/7")
        self.assertIsNotNone(dynamics)
        self.assertEqual(dynamics.profile, InjectionProfile.BOLUS)
        self.assertEqual(dynamics.duration, Decimal("5"))
        self.assertEqual(dynamics.duration_unit, TimeUnit.M)
        self.assertEqual(dynamics.injection_current, Decimal("5"))
        self.assertEqual(dynamics.injection_current_unit, CurrentUnit.UA)
        self.assertEqual(dynamics.alternating_current, "7/7")
        self.assertIsNone(dynamics.volume)

    def test_map_first_injection_coordinate_system(self):
        """Test first injection coordinate system mapping"""
        # Case 1: LAMBDA_ARID
        test_data = deepcopy(self.injection_data)
        test_data["Virus_x0020_A_x002f_P"] = "Lambda -1.6"
        test_data["Virus_x0020_M_x002f_L"] = "-3.3"
        test_data["Virus_x0020_D_x002f_V"] = "4.3"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        coord_sys = mapper.aind_inj1_coordinates_reference
        self.assertIsNotNone(coord_sys)
        self.assertEqual(coord_sys.name, "LAMBDA_ARID")
        self.assertEqual(coord_sys.origin, Origin.LAMBDA)

        # Case 2: BREGMA_ARI
        test_data["Virus_x0020_A_x002f_P"] = "-1.6"
        test_data["Virus_x0020_D_x002f_V"] = None

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertEqual(
            mapper.aind_inj1_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARI,
        )

        # Case 3: BREGMA_ARID
        test_data["Virus_x0020_D_x002f_V"] = "4.3"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertEqual(
            mapper.aind_inj1_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARID,
        )

        # Case 4: None
        test_data["Virus_x0020_A_x002f_P"] = None
        test_data["Virus_x0020_M_x002f_L"] = None

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertIsNone(mapper.aind_inj1_coordinates_reference)

    def test_map_second_injection_properties(self):
        """Test second injection coordinate and property mapping"""
        test_data = deepcopy(self.injection_data)
        test_data["AP2ndInj"] = "-3.05"
        test_data["ML2ndInj"] = "-0.6"
        test_data["DV2ndInj"] = "4.3"
        test_data["Hemisphere2ndInj"] = "Left"
        test_data["Inj2Type"] = "Iontophoresis"
        test_data["Inj2Vol"] = "500"
        test_data["Inj2LenghtofTime"] = "4min"
        test_data["Inj2Current"] = "5 uA"
        test_data["Inj2AlternatingTime"] = "7/7"
        test_data["SecondInjectionWeightAfter"] = "19.3"
        test_data["SecondInjectionWeightBefore"] = "19.2"
        test_data["SecondInjectionIsoDuration"] = "45min"
        test_data["WorkStation2ndInjection"] = "SWS 4"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertEqual(mapper.aind_ap2nd_inj, Decimal("-3.05"))
        self.assertEqual(mapper.aind_ml2nd_inj, Decimal("-0.6"))
        self.assertEqual(mapper.aind_dv2nd_inj, Decimal("4.3"))
        self.assertEqual(
            mapper.aind_inj2_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARID,
        )
        self.assertEqual(mapper.aind_inj2_vol[0], Decimal("500"))

    def test_map_second_injection_coordinate_system(self):
        """Test second injection coordinate system mapping for all cases"""
        # Case 1: LAMBDA_ARID
        test_data = deepcopy(self.injection_data)
        test_data["AP2ndInj"] = "Lambda -3.05"
        test_data["ML2ndInj"] = "-0.6"
        test_data["DV2ndInj"] = "4.3"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        coord_sys = mapper.aind_inj2_coordinates_reference
        self.assertIsNotNone(coord_sys)
        self.assertEqual(coord_sys.name, "LAMBDA_ARID")
        self.assertEqual(coord_sys.origin, Origin.LAMBDA)

        # Case 2: BREGMA_ARI
        test_data["AP2ndInj"] = "-3.05"
        test_data["DV2ndInj"] = None

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertEqual(
            mapper.aind_inj2_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARI,
        )

        # Case 3: BREGMA_ARID
        test_data["DV2ndInj"] = "4.3"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertEqual(
            mapper.aind_inj2_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARID,
        )

        # Case 4: None
        test_data["AP2ndInj"] = None
        test_data["ML2ndInj"] = None

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertIsNone(mapper.aind_inj2_coordinates_reference)

    def test_map_second_injection_procedure(self):
        """Test creation of second BrainInjection procedure"""
        test_data = deepcopy(self.injection_data)
        test_data["AP2ndInj"] = "-3.05"
        test_data["ML2ndInj"] = "-0.6"
        test_data["Inj2Type"] = "Iontophoresis"
        test_data["Inj2Vol"] = "500"
        test_data["Inj2LenghtofTime"] = "4min"
        test_data["Inj2Current"] = "5 uA"
        test_data["Inj2AlternatingTime"] = "7/7"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        injection = mapper.get_second_injection_procedure()
        self.assertIsInstance(injection, BrainInjection)
        self.assertEqual(injection.object_type, "Brain injection")
        self.assertTrue(mapper.has_second_injection_procedure)

    def test_map_second_nanoject_injection(self):
        """Test second injection with Nanoject type"""
        test_data = deepcopy(self.injection_data)
        test_data["AP2ndInj"] = "-3.05"
        test_data["ML2ndInj"] = "-0.6"
        test_data["DV2ndInj"] = "4.3"
        test_data["Inj2Type"] = "Nanoject (Pressure)"
        test_data["Inj2Vol"] = "500"
        test_data["Inj2LenghtofTime"] = "4min"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        dynamics = mapper.aind_inj2_dynamics

        self.assertEqual(mapper.aind_inj2_type, InjectionType.NANOJECT)
        self.assertEqual(mapper.aind_inj2_vol[0], Decimal("500"))
        self.assertEqual(mapper.aind_inj2_lenghtof_time, Decimal("4"))
        self.assertEqual(dynamics.volume, [Decimal("500")])

    def test_map_coordinate_system_without_dv(self):
        """Test coordinate system mapping when DV is missing"""
        test_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "AP2ndInj": "1.0",
            "ML2ndInj": "2.0",
        }
        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertEqual(
            mapper.aind_inj2_coordinates_reference,
            CoordinateSystemLibrary.BREGMA_ARI,
        )


class TestNSB2019FiberImplantMapping(TestCase):
    """Tests fiber implant/probe implant mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.fiber_data = {
            "FileSystemObjectType": 0,
            "Id": 5554,
            "Procedure": "HP+Injection+Optic Fiber Implant",
            "FiberImplant1": True,
            "FiberImplant1DV": "4.2",
            "FiberImplant2": True,
            "FiberImplant2DV": "4.2",
            "Virus_x0020_A_x002f_P": "-1.6",
            "Virus_x0020_M_x002f_L": "-3.3",
            "Inj1Angle_v2": "0",
            "Inj2Angle_v2": "90",
            "Date_x0020_of_x0020_Surgery": "2022-12-06T08:00:00Z",
            "IACUC_x0020_Protocol_x0020__x002": "2115",
        }
        cls.nsb_model = NSB2019List.model_validate(cls.fiber_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)

    def test_map_fiber_implant_flags(self):
        """Test fiber implant presence flags"""
        self.assertTrue(self.mapper.aind_fiber_implant1)
        self.assertTrue(self.mapper.aind_fiber_implant2)

    def test_map_fiber_implant_depths(self):
        """Test fiber implant depth mapping"""
        self.assertEqual(self.mapper.aind_fiber_implant1_dv, Decimal("4.2"))
        self.assertEqual(self.mapper.aind_fiber_implant2_dv, Decimal("4.2"))

    def test_has_fiber_implant_procedure(self):
        """Test detection of fiber implant procedure"""
        self.assertTrue(self.mapper.has_fiber_implant_procedure)

    def test_map_fiber_implant_procedures(self):
        """Test creation of ProbeImplant procedures"""
        fiber_implants = self.mapper.get_fiber_implants()
        self.assertIsInstance(fiber_implants, list)
        self.assertEqual(len(fiber_implants), 2)
        for implant in fiber_implants:
            self.assertIsInstance(implant, ProbeImplant)
            self.assertIsInstance(implant.implanted_device, FiberProbe)
            self.assertIsInstance(implant.device_config, ProbeConfig)
            self.assertIsInstance(implant.device_config.transform, list)
        self.assertEqual(fiber_implants[0].implanted_device.name, "Probe A")
        self.assertEqual(fiber_implants[1].implanted_device.name, "Probe B")


class TestNSB2019SurgeryIntegration(TestCase):
    """Tests complete Surgery object creation"""

    @classmethod
    def setUpClass(cls):
        """Create comprehensive test data"""
        cls.full_surgery_data = {
            "FileSystemObjectType": 0,
            "Id": 5554,
            "Date_x0020_of_x0020_Surgery": "2022-12-06T08:00:00Z",
            "Weight_x0020_before_x0020_Surger": "19.1",
            "Weight_x0020_after_x0020_Surgery": "19.2",
            "HpWorkStation": "SWS 3",
            "IACUC_x0020_Protocol_x0020__x002": "2115",
            "HeadpostType": "AI Straight Headbar",
            "CraniotomyType": "Visual Cortex 5mm",
            "Procedure": "HP+Injection+Optic Fiber Implant",
            "Virus_x0020_A_x002f_P": "-1.6",
            "Virus_x0020_M_x002f_L": "-3.3",
            "Virus_x0020_D_x002f_V": "4.3",
            "Virus_x0020_Hemisphere": "Left",
            "Inj1Type": "Nanoject (Pressure)",
            "Inj1Vol": "400",
            "Inj1LenghtofTime": "5min",
            "Date1stInjection": "2022-12-06T08:00:00Z",
            "FirstInjectionWeightBefor": "19.1",
            "FirstInjectionWeightAfter": "19.2",
            "FirstInjectionIsoDuration": "1 hour",
            "FiberImplant1": True,
            "FiberImplant1DV": "4.2",
            "Breg2Lamb": "4",
            "HPIsoLevel": "1.5",
            "AuthorId": 187,
            "Round1InjIsolevel": None,
            "Round2InjIsolevel": None,
        }
        cls.nsb_model = NSB2019List.model_validate(cls.full_surgery_data)
        cls.mapper = MappedNSBList(nsb=cls.nsb_model)
        cls.surgeries = cls.mapper.get_surgeries()

    def test_get_surgeries_basic_structure(self):
        """Test basic surgery creation"""
        self.assertIsInstance(self.surgeries, list)
        self.assertGreater(len(self.surgeries), 0)
        self.assertFalse(self.mapper.has_unknown_surgery)

        for surgery in self.surgeries:
            self.assertIsInstance(surgery, Surgery)
            self.assertIsNotNone(surgery.experimenters)
            self.assertEqual(surgery.experimenters[0], "NSB-187")

    def test_has_unknown_surgery_edge_case(self):
        """Test unknown surgery detection for edge case"""
        test_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
        }
        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertFalse(mapper.has_unknown_surgery)

    def test_get_surgeries_with_multiple_procedures(self):
        """Test surgery with multiple procedures"""
        combined_surgery = next(
            (
                s
                for s in self.surgeries
                if any(isinstance(p, Headframe) for p in s.procedures)
                and any(isinstance(p, ProbeImplant) for p in s.procedures)
            ),
            None,
        )
        self.assertIsNotNone(combined_surgery)
        self.assertIsNotNone(combined_surgery.anaesthesia)
        self.assertEqual(
            combined_surgery.anaesthesia.anaesthetic_type, "isoflurane"
        )

    def test_get_surgeries_with_injection(self):
        """Test surgery with injection procedure"""
        injection_surgery = next(
            (
                s
                for s in self.surgeries
                if any(isinstance(p, BrainInjection) for p in s.procedures)
            ),
            None,
        )

        self.assertIsNotNone(injection_surgery)
        self.assertIsNotNone(injection_surgery.start_date)
        self.assertIsNotNone(injection_surgery.measured_coordinates)

    def test_get_surgeries_with_validation_error(self):
        """Test surgery creation when validation error occurs"""

        test_data = deepcopy(self.full_surgery_data)
        test_data["Date1stInjection"] = None
        test_data["Virus_x0020_A_x002f_P"] = "-1.6"
        test_data["Virus_x0020_M_x002f_L"] = "-3.3"
        test_data["Virus_x0020_D_x002f_V"] = "4.3"
        test_data["Inj1Type"] = "Nanoject (Pressure)"
        test_data["Inj1Vol"] = "400"
        test_data["Inj1LenghtofTime"] = "5min"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        injection_surgery = next(
            (
                s
                for s in surgeries
                if any(isinstance(p, BrainInjection) for p in s.procedures)
            ),
            None,
        )

        self.assertIsNotNone(injection_surgery)
        self.assertIsInstance(injection_surgery, Surgery)
        self.assertIsNone(
            injection_surgery.start_date
        )  # Should be None due to missing date
        self.assertEqual(len(injection_surgery.procedures), 1)
        self.assertIsInstance(injection_surgery.procedures[0], BrainInjection)

    def test_get_surgeries_with_craniotomy(self):
        """Test surgery with craniotomy procedure"""
        test_data = deepcopy(self.full_surgery_data)
        test_data["Procedure"] = "HP+C CAM"
        test_data["HPDurotomy"] = "No"
        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()
        craniotomy = next(
            (p for p in surgeries[0].procedures if isinstance(p, Craniotomy)),
            None,
        )
        self.assertIsNotNone(craniotomy)
        self.assertEqual(craniotomy.craniotomy_type, CraniotomyType.CIRCLE)
        self.assertEqual(craniotomy.size, Decimal(5))

    def test_procedure_flags(self):
        """Test procedure presence flags"""
        self.assertTrue(self.mapper.has_injection_procedure)
        self.assertFalse(self.mapper.has_craniotomy_procedure)
        self.assertTrue(self.mapper.has_head_frame_procedure)
        self.assertTrue(self.mapper.has_fiber_implant_procedure)

    def test_unknown_surgery_handling(self):
        """Test handling of unknown surgery"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Date_x0020_of_x0020_Surgery": "2022-12-06T08:00:00Z",
        }
        nsb_model = NSB2019List.model_validate(nsb_data)
        mapper = MappedNSBList(nsb=nsb_model)

        self.assertTrue(mapper.has_unknown_surgery)
        surgeries = mapper.get_surgeries()
        self.assertEqual(len(surgeries), 1)

    def test_get_surgeries_with_second_injection_valid(self):
        """Test surgery creation with valid second injection"""
        test_data = deepcopy(self.full_surgery_data)
        # Add second injection data
        test_data["AP2ndInj"] = "-3.05"
        test_data["ML2ndInj"] = "-0.6"
        test_data["DV2ndInj"] = "4.3"
        test_data["Hemisphere2ndInj"] = "Left"
        test_data["Inj2Type"] = "Nanoject (Pressure)"
        test_data["Inj2Vol"] = "500"
        test_data["Inj2LenghtofTime"] = "4min"
        test_data["Date2ndInjection"] = "2022-12-07T08:00:00Z"
        test_data["SecondInjectionWeightBefore"] = "19.2"
        test_data["SecondInjectionWeightAfter"] = "19.3"
        test_data["SecondInjectionIsoDuration"] = "1 hour"
        test_data["WorkStation2ndInjection"] = "SWS 4"
        test_data["Round2InjIsolevel"] = "1.50"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()

        # Should have 3 surgeries: HP+Craniotomy+Fiber, 1st injection, 2nd injection
        self.assertEqual(len(surgeries), 3)

        # Find the second injection surgery
        second_injection_surgery = surgeries[2]

        # Verify it's a valid Surgery object with BrainInjection
        self.assertIsInstance(second_injection_surgery, Surgery)
        self.assertEqual(len(second_injection_surgery.procedures), 1)
        self.assertIsInstance(
            second_injection_surgery.procedures[0], BrainInjection
        )

        # Verify second injection specific fields
        self.assertEqual(
            str(second_injection_surgery.start_date), "2022-12-07"
        )
        self.assertEqual(second_injection_surgery.animal_weight_prior, 19.2)
        self.assertEqual(second_injection_surgery.animal_weight_post, 19.3)
        self.assertEqual(second_injection_surgery.workstation_id, "SWS 4")

        # Verify anaesthesia
        self.assertIsNotNone(second_injection_surgery.anaesthesia)
        self.assertEqual(
            second_injection_surgery.anaesthesia.anaesthetic_type, "isoflurane"
        )
        self.assertEqual(second_injection_surgery.anaesthesia.duration, 60.0)
        self.assertEqual(second_injection_surgery.anaesthesia.level, 1.5)

        # Verify measured coordinates
        self.assertIsNotNone(second_injection_surgery.measured_coordinates)
        self.assertIn(
            Origin.BREGMA, second_injection_surgery.measured_coordinates
        )

        # Verify coordinate system
        self.assertEqual(
            second_injection_surgery.coordinate_system,
            CoordinateSystemLibrary.BREGMA_ARID,
        )

        # Verify injection dynamics
        injection = second_injection_surgery.procedures[0]
        self.assertEqual(len(injection.dynamics), 1)
        print(injection.dynamics)
        self.assertEqual(injection.dynamics[0].volume, [Decimal("500")])
        self.assertEqual(injection.dynamics[0].volume_unit, VolumeUnit.NL)
        self.assertEqual(injection.dynamics[0].duration, Decimal("4"))

    def test_get_surgeries_with_second_injection_validation_error(self):
        """Test second injection surgery creation with missing start_date (validation error)"""
        test_data = deepcopy(self.full_surgery_data)
        test_data["AP2ndInj"] = "-3.05"
        test_data["ML2ndInj"] = "-0.6"
        test_data["DV2ndInj"] = "4.3"
        test_data["Inj2Type"] = "Iontophoresis"
        test_data["Inj2Vol"] = "500"
        test_data["Inj2LenghtofTime"] = "4min"
        test_data["Inj2Current"] = "5 uA"
        test_data["Inj2AlternatingTime"] = "7/7"
        test_data["Date2ndInjection"] = None
        test_data["SecondInjectionWeightBefore"] = "19.2"
        test_data["SecondInjectionWeightAfter"] = "19.3"
        test_data["SecondInjectionIsoDuration"] = "45min"
        test_data["WorkStation2ndInjection"] = "SWS 4"

        nsb_model = NSB2019List.model_validate(test_data)
        mapper = MappedNSBList(nsb=nsb_model)
        surgeries = mapper.get_surgeries()

        self.assertEqual(len(surgeries), 3)
        second_injection_surgery = surgeries[2]

        self.assertIsInstance(second_injection_surgery, Surgery)
        self.assertIsNone(second_injection_surgery.start_date)
        self.assertEqual(len(second_injection_surgery.procedures), 1)
        self.assertIsInstance(
            second_injection_surgery.procedures[0], BrainInjection
        )
        self.assertEqual(
            second_injection_surgery.animal_weight_prior, Decimal("19.2")
        )
        self.assertEqual(
            second_injection_surgery.animal_weight_post, Decimal("19.3")
        )
        self.assertEqual(second_injection_surgery.workstation_id, "SWS 4")


class TestNSB2019CoordinateMapping(TestCase):
    """Tests coordinate and transform mapping"""

    def test_map_measured_coordinates_bregma(self):
        """Test measured coordinates with BREGMA"""
        coords = MappedNSBList.get_measured_coordinates(
            b2l_dist=Decimal("4.5"), coordinate_system_name="BREGMA_ARI"
        )
        self.assertIsNotNone(coords)
        from aind_data_schema_models.coordinates import Origin

        self.assertIn(Origin.BREGMA, coords)

    def test_map_measured_coordinates_lambda(self):
        """Test measured coordinates with LAMBDA"""
        coords = MappedNSBList.get_measured_coordinates(
            b2l_dist=Decimal("4.5"), coordinate_system_name="LAMBDA_ARI"
        )
        self.assertIsNotNone(coords)
        from aind_data_schema_models.coordinates import Origin

        self.assertIn(Origin.LAMBDA, coords)

    def test_map_measured_coordinates_none(self):
        """Test measured coordinates with None"""
        coords = MappedNSBList.get_measured_coordinates(
            b2l_dist=None, coordinate_system_name=None
        )
        self.assertIsNone(coords)

    def test_map_transform_without_depth(self):
        """Test transform creation without depth"""
        transform = MappedNSBList._get_transform(
            angle=Decimal("10"),
            ml=Decimal("2.0"),
            ap=Decimal("1.5"),
            depth=None,
        )
        self.assertIsInstance(transform, list)
        self.assertEqual(len(transform), 2)

    def test_map_transform_with_depth(self):
        """Test transform creation with depth"""
        transform = MappedNSBList._get_transform(
            angle=Decimal("10"),
            ml=Decimal("2.0"),
            ap=Decimal("1.5"),
            depth=Decimal("3.0"),
        )
        self.assertIsInstance(transform, list)
        self.assertEqual(len(transform), 2)


class TestNSB2019StringParsers(TestCase):
    """Tests text field parsers in NSB2019Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Create blank mapper for parser testing"""
        cls.blank_model = MappedNSBList(
            nsb=NSB2019List.model_validate(
                {"FileSystemObjectType": 0, "Id": 0}
            )
        )

    def test_parse_ap_str(self):
        """Tests parsing of AP coordinate values"""
        self.assertEqual(
            self.blank_model._parse_ap_str("-1.06"), Decimal("-1.06")
        )
        self.assertEqual(self.blank_model._parse_ap_str("1"), Decimal("1.0"))
        self.assertEqual(
            self.blank_model._parse_ap_str("-3.8mm"), Decimal("-3.8")
        )
        self.assertIsNone(self.blank_model._parse_ap_str("calamus -0.44"))
        self.assertIsNone(self.blank_model._parse_ap_str(None))

    def test_parse_ml_str(self):
        """Tests parsing of ML coordinate values"""
        self.assertEqual(self.blank_model._parse_ml_str("3.4"), Decimal("3.4"))
        self.assertEqual(
            self.blank_model._parse_ml_str("-2.3 mm"), Decimal("-2.3")
        )
        self.assertEqual(
            self.blank_model._parse_ml_str(".35"), Decimal("0.35")
        )
        self.assertIsNone(self.blank_model._parse_ml_str("-2.7mm (Left)"))
        self.assertIsNone(self.blank_model._parse_ml_str(None))

    def test_parse_dv_str(self):
        """Tests parsing of DV coordinate values"""
        self.assertEqual(
            self.blank_model._parse_dv_str("3.38"), Decimal("3.38")
        )
        self.assertEqual(
            self.blank_model._parse_dv_str("0.6mm"), Decimal("0.6")
        )
        self.assertEqual(
            self.blank_model._parse_dv_str("+3.6"), Decimal("3.6")
        )
        self.assertIsNone(self.blank_model._parse_dv_str("2.2, 2.60"))
        self.assertIsNone(self.blank_model._parse_dv_str(None))

    def test_parse_weight_str(self):
        """Tests parsing of animal weight values"""
        self.assertEqual(
            self.blank_model._parse_weight_str("19.1"), Decimal("19.1")
        )
        self.assertEqual(
            self.blank_model._parse_weight_str("30."), Decimal("30.0")
        )
        self.assertIsNone(self.blank_model._parse_weight_str("20/0"))
        self.assertIsNone(self.blank_model._parse_weight_str(None))

    def test_parse_iso_dur_str(self):
        """Tests parsing of isoflurane duration values"""

        self.assertEqual(
            self.blank_model._parse_iso_dur_str("1"), Decimal("60.0")
        )
        self.assertEqual(
            self.blank_model._parse_iso_dur_str("1:45"), Decimal("105.0")
        )
        self.assertEqual(
            self.blank_model._parse_iso_dur_str("2 hours"), Decimal("120.0")
        )
        self.assertEqual(
            self.blank_model._parse_iso_dur_str("0.75"), Decimal("45.0")
        )
        self.assertEqual(
            self.blank_model._parse_iso_dur_str("2.5 hour"), Decimal("150.0")
        )

        self.assertIsNone(self.blank_model._parse_iso_dur_str("6 hours"))
        self.assertIsNone(self.blank_model._parse_iso_dur_str("5:30"))
        self.assertIsNone(self.blank_model._parse_iso_dur_str("45"))
        self.assertIsNone(self.blank_model._parse_iso_dur_str("1:"))
        self.assertIsNone(self.blank_model._parse_iso_dur_str("abc:def"))
        self.assertIsNone(self.blank_model._parse_iso_dur_str(None))

    def test_parse_angle_str(self):
        """Tests parsing of injection angle values"""
        self.assertEqual(
            self.blank_model._parse_angle_str("0"), Decimal("0.0")
        )
        self.assertEqual(
            self.blank_model._parse_angle_str("-10"), Decimal("-10.0")
        )
        self.assertEqual(
            self.blank_model._parse_angle_str("0 degree"), Decimal("0.0")
        )
        self.assertIsNone(self.blank_model._parse_angle_str("normal"))
        self.assertIsNone(self.blank_model._parse_angle_str(None))

    def test_parse_current_str(self):
        """Tests parsing of injection current values"""
        self.assertEqual(
            self.blank_model._parse_current_str("5uA"), Decimal("5.0")
        )
        self.assertEqual(
            self.blank_model._parse_current_str("3 uA"), Decimal("3.0")
        )
        self.assertIsNone(self.blank_model._parse_current_str("5min"))
        self.assertIsNone(self.blank_model._parse_current_str(None))

    def test_parse_alt_time_str(self):
        """Tests parsing of alternating time values"""
        self.assertEqual(
            self.blank_model._parse_alt_time_str("7/7"), Decimal("7.0")
        )
        self.assertEqual(
            self.blank_model._parse_alt_time_str("7 seconds"), Decimal("7.0")
        )
        self.assertIsNone(self.blank_model._parse_alt_time_str("30sec"))
        self.assertIsNone(self.blank_model._parse_alt_time_str(None))

    def test_parse_length_of_time_str(self):
        """Tests parsing of duration/length of time values"""
        self.assertEqual(
            self.blank_model._parse_length_of_time_str("5min"), Decimal("5.0")
        )
        self.assertEqual(
            self.blank_model._parse_length_of_time_str("10 minutes"),
            Decimal("10.0"),
        )
        self.assertEqual(
            self.blank_model._parse_length_of_time_str("2.5min"),
            Decimal("2.5"),
        )
        self.assertIsNone(self.blank_model._parse_length_of_time_str("30 sec"))
        self.assertIsNone(self.blank_model._parse_length_of_time_str(None))

    def test_parse_inj_vol_str(self):
        """Tests parsing of injection volume values"""
        self.assertEqual(
            self.blank_model._parse_inj_vol_str("200 nL"), Decimal("200.0")
        )
        self.assertEqual(
            self.blank_model._parse_inj_vol_str("500nl"), Decimal("500.0")
        )
        self.assertEqual(
            self.blank_model._parse_inj_vol_str("400"), Decimal("400.0")
        )
        self.assertIsNone(self.blank_model._parse_inj_vol_str("1uL (1000nl)"))
        self.assertIsNone(self.blank_model._parse_inj_vol_str(None))

    def test_basic_float_parser(self):
        """Tests parsing of basic float strings"""
        self.assertEqual(self.blank_model._parse_basic_float_str("1.5"), 1.5)
        self.assertEqual(self.blank_model._parse_basic_float_str("0"), 0.0)
        self.assertIsNone(self.blank_model._parse_basic_float_str("invalid"))
        self.assertIsNone(self.blank_model._parse_basic_float_str(None))

    def test_basic_decimal_parser(self):
        """Tests parsing of basic decimal strings"""
        self.assertEqual(
            self.blank_model._parse_basic_decimal_str("1.5"), Decimal("1.5")
        )
        self.assertEqual(
            self.blank_model._parse_basic_decimal_str("0"), Decimal("0")
        )
        self.assertIsNone(self.blank_model._parse_basic_decimal_str("invalid"))
        self.assertIsNone(self.blank_model._parse_basic_decimal_str(None))


if __name__ == "__main__":
    unittest_main()
