"""Tests LAS 2020 data model is parsed correctly"""

from copy import deepcopy
from decimal import Decimal
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.components.injection_procedures import (
    Injection,
    NonViralMaterial,
)
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema_models.coordinates import AnatomicalRelative
from aind_data_schema_models.mouse_anatomy import InjectionTargets
from aind_data_schema_models.units import TimeUnit, VolumeUnit
from aind_sharepoint_service_async_client.models.las2020_list import (
    Las2020List,
    LASDoseroute,
)

from aind_metadata_service_server.mappers.las2020 import (
    LASProcedure,
    MappedLASList,
)


class TestLAS2020BasicMapping(TestCase):
    """Tests basic LAS2020 mapping functionality"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.basic_las_data = {
            "FileSystemObjectType": 0,
            "Id": 6709,
            "AuthorId": 5358,
            "Protocol": "2212 - Investigating Brain States",
            "nStart_x0020_Date": "2024-06-21T07:00:00Z",
            "ReqPro1": "Tissue Collection",
            "ReqPro2": "Dosing",
        }
        cls.las_model = Las2020List.model_validate(cls.basic_las_data)
        cls.mapper = MappedLASList(las=cls.las_model)

    def test_map_author_id(self):
        """Test author ID mapping"""
        test_data = {"FileSystemObjectType": 0, "Id": 1}
        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)
        self.assertIsNone(mapper.aind_author_id)
        self.assertEqual(self.mapper.aind_author_id, "LAS-5358")

    def test_map_protocol(self):
        """Test IACUC protocol mapping"""
        self.assertEqual(self.mapper.aind_protocol, "2212")

    def test_map_start_date(self):
        """Test start date mapping"""
        self.assertIsNotNone(self.mapper.aind_n_start_date)
        self.assertEqual(str(self.mapper.aind_n_start_date), "2024-06-21")

    def test_map_requested_procedures(self):
        """Test requested procedure mappings"""
        self.assertEqual(
            self.mapper.aind_req_pro1, LASProcedure.TISSUE_COLLECTION
        )
        self.assertEqual(self.mapper.aind_req_pro2, LASProcedure.DOSING)
        self.assertIsNone(self.mapper.aind_req_pro3)


class TestLAS2020IPInjectionMapping(TestCase):
    """Tests intraperitoneal injection procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.ip_injection_data = {
            "FileSystemObjectType": 0,
            "Id": 6709,
            "AuthorId": 5358,
            "Protocol": "2212 - Investigating Brain States",
            "nStart_x0020_Date": "2024-06-21T07:00:00Z",
            "ReqPro1": "Dosing",
            "doseRoute": "Intraperitoneal (IP)",
            "doseSub": "Heparin 1000U/mL",
            "dosevolume": "70.4 uL",
            "doseduration": "30 s",
        }
        cls.las_model = Las2020List.model_validate(cls.ip_injection_data)
        cls.mapper = MappedLASList(las=cls.las_model)

    def test_map_dose_route(self):
        """Test dose route mapping"""
        self.assertEqual(
            self.mapper.aind_dose_route, LASDoseroute.INTRAPERITONEAL_IP
        )

    def test_map_dose_substance(self):
        """Test dose substance mapping"""
        dose_sub = self.mapper.aind_dose_sub
        self.assertIsInstance(dose_sub, NonViralMaterial)
        self.assertEqual(dose_sub.name, "Heparin")
        self.assertEqual(dose_sub.concentration, Decimal("1000"))
        self.assertEqual(dose_sub.concentration_unit, "u/ml")

    def test_map_dose_volume(self):
        """Test dose volume mapping"""
        self.assertEqual(self.mapper.aind_dosevolume, Decimal("70.4"))

    def test_map_dose_duration(self):
        """Test dose duration mapping"""
        self.assertEqual(self.mapper.aind_doseduration, Decimal("30"))
        self.assertEqual(self.mapper.aind_doseduration_unit, TimeUnit.S)

    def test_has_ip_injection(self):
        """Test detection of IP injection procedure"""
        self.assertTrue(self.mapper.has_ip_injection())

    def test_map_ip_injection_procedure(self):
        """Test creation of IP Injection procedure"""
        surgery = self.mapper.get_surgery(subject_id="000000")
        self.assertIsNotNone(surgery)

        ip_injection = next(
            (p for p in surgery.procedures if isinstance(p, Injection)), None
        )
        self.assertIsNotNone(ip_injection)
        self.assertEqual(
            ip_injection.targeted_structure, InjectionTargets.INTRAPERITONEAL
        )


class TestLAS2020RetroOrbitalInjectionMapping(TestCase):
    """Tests retro-orbital injection procedure mapping"""

    @classmethod
    def setUpClass(cls):
        """Create test data once for all tests"""
        cls.ro_injection_data = {
            "FileSystemObjectType": 0,
            "Id": 6709,
            "AuthorId": 5358,
            "Protocol": "2212 - Investigating Brain States",
            "nStart_x0020_Date": "2024-06-21T07:00:00Z",
            "ReqPro1": "Retro-Orbital Injection",
            "nROID1": "000000",
            "roEye1": "Behind Right",
            "roVol1": "100",
            "roSub1": "AAV-PHP.eB",
            "roLot1": "LOT123",
            "roGC1": "1e13",
            "roTite1": "1e12",
            "roTube1": "Tube-A",
            "roBox1": "Box-1",
        }
        cls.las_model = Las2020List.model_validate(cls.ro_injection_data)
        cls.mapper = MappedLASList(las=cls.las_model)

    def test_map_ro_animal_id(self):
        """Test RO animal ID mapping"""
        self.assertEqual(self.mapper.aind_n_roid1, "000000")

    def test_map_ro_eye(self):
        """Test RO injection eye mapping"""
        self.assertEqual(self.mapper.aind_ro_eye1, AnatomicalRelative.RIGHT)

    def test_map_ro_volume(self):
        """Test RO injection volume mapping"""
        self.assertEqual(self.mapper.aind_ro_vol1, Decimal("100"))

    def test_map_ro_substance(self):
        """Test RO injection substance mapping"""
        self.assertEqual(self.mapper.aind_ro_sub1, "AAV-PHP.eB")

    def test_map_ro_lot(self):
        """Test RO injection lot mapping"""
        self.assertEqual(self.mapper.aind_ro_lot1, "LOT123")

    def test_map_ro_genome_copy(self):
        """Test RO injection genome copy mapping"""
        self.assertEqual(self.mapper.aind_ro_gc1, "1e13")

    def test_map_ro_titer(self):
        """Test RO injection titer mapping"""
        self.assertEqual(self.mapper.aind_ro_tite1, "1e12")

    def test_map_ro_tube_and_box(self):
        """Test RO injection tube and box labels"""
        self.assertEqual(self.mapper.aind_ro_tube1, "Tube-A")
        self.assertEqual(self.mapper.aind_ro_box1, "Box-1")

    def test_has_ro_injection(self):
        """Test detection of RO injection procedure"""
        self.assertTrue(self.mapper.has_ro_injection())

    def test_map_ro_injection_info(self):
        """Test RO injection info compilation"""
        ro_info = self.mapper.map_ro_injection_info(ro_num=1)
        self.assertIsNotNone(ro_info)
        self.assertEqual(ro_info.animal_id, "000000")
        self.assertEqual(ro_info.injection_eye, AnatomicalRelative.RIGHT)
        self.assertEqual(ro_info.injection_volume, Decimal("100"))
        self.assertEqual(ro_info.tube_label, "Tube-A")
        self.assertEqual(ro_info.box_label, "Box-1")
        self.assertEqual(len(ro_info.injectable_materials), 1)

    def test_map_ro_injection_procedure(self):
        """Test creation of RO Injection procedure"""
        surgery = self.mapper.get_surgery(subject_id="000000")
        self.assertIsNotNone(surgery)

        ro_injection = next(
            (p for p in surgery.procedures if isinstance(p, Injection)), None
        )
        self.assertIsNotNone(ro_injection)
        self.assertEqual(
            ro_injection.targeted_structure, InjectionTargets.RETRO_ORBITAL
        )
        self.assertIn(AnatomicalRelative.RIGHT, ro_injection.relative_position)

    def test_map_multiple_ro_materials(self):
        """Test RO injection with multiple materials (a, b, c, d suffixes)"""
        test_data = deepcopy(self.ro_injection_data)
        test_data["roSub1b"] = "AAV-PHP.S"
        test_data["roLot1b"] = "LOT456"
        test_data["roGC1b"] = "2e13"
        test_data["roTite1b"] = "2e12"

        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)

        ro_info = mapper.map_ro_injection_info(ro_num=1)
        self.assertEqual(len(ro_info.injectable_materials), 2)
        self.assertEqual(
            ro_info.injectable_materials[1].substance, "AAV-PHP.S"
        )


class TestLAS2020SurgeryIntegration(TestCase):
    """Tests complete Surgery object creation"""

    @classmethod
    def setUpClass(cls):
        """Create comprehensive test data"""
        cls.full_surgery_data = {
            "FileSystemObjectType": 0,
            "Id": 6709,
            "AuthorId": 5358,
            "Protocol": "2212 - Investigating Brain States",
            "nStart_x0020_Date": "2024-06-21T07:00:00Z",
            "ReqPro1": "Dosing",
            "ReqPro2": "Retro-Orbital Injection",
            "doseRoute": "Intraperitoneal (IP)",
            "doseSub": "Heparin 1000U/mL",
            "dosevolume": "70.4",
            "doseduration": "30 s",
            "nROID1": "000000",
            "roEye1": "Behind Right",
            "roVol1": "100",
            "roSub1": "AAV-PHP.eB",
        }
        cls.las_model = Las2020List.model_validate(cls.full_surgery_data)
        cls.mapper = MappedLASList(las=cls.las_model)

    def test_get_surgery_basic_structure(self):
        """Test basic surgery creation"""
        surgery = self.mapper.get_surgery(subject_id="000000")
        self.assertIsInstance(surgery, Surgery)
        self.assertIsNotNone(surgery.experimenters)
        self.assertEqual(surgery.experimenters[0], "LAS-5358")
        self.assertEqual(surgery.ethics_review_id, "2212")

    def test_get_surgery_with_multiple_procedures(self):
        """Test surgery with IP and RO injections"""
        surgery = self.mapper.get_surgery(subject_id="000000")
        self.assertEqual(len(surgery.procedures), 2)
        self.assertEqual(
            surgery.procedures[0].targeted_structure,
            InjectionTargets.INTRAPERITONEAL,
        )
        self.assertEqual(
            surgery.procedures[1].targeted_structure,
            InjectionTargets.RETRO_ORBITAL,
        )

    def test_get_surgery_no_procedures(self):
        """Test surgery returns None when no procedures"""
        test_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "AuthorId": 5358,
            "Protocol": "2207 - In Vitro Brain Stimulation",
        }
        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)

        surgery = mapper.get_surgery(subject_id="000000")
        self.assertIsNone(surgery)

    def test_get_surgery_wrong_subject_id(self):
        """Test surgery with wrong subject ID for RO injection"""
        surgery = self.mapper.get_surgery(subject_id="999999")
        self.assertEqual(len(surgery.procedures), 1)
        self.assertEqual(
            surgery.procedures[0].targeted_structure,
            InjectionTargets.INTRAPERITONEAL,
        )


class TestLAS2020StringParsers(TestCase):
    """Tests text field parsers in LAS2020Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Create blank mapper for parser testing"""
        cls.blank_model = MappedLASList(
            las=Las2020List.model_validate(
                {"FileSystemObjectType": 0, "Id": 0}
            )
        )

    def test_parse_basic_decimal_str(self):
        """Test basic decimal string parsing"""
        self.assertEqual(
            self.blank_model._parse_basic_decimal_str("0.25"), Decimal("0.25")
        )
        self.assertEqual(
            self.blank_model._parse_basic_decimal_str("100"), Decimal("100")
        )
        self.assertIsNone(self.blank_model._parse_basic_decimal_str("abc"))
        self.assertIsNone(self.blank_model._parse_basic_decimal_str(None))

    def test_parse_dose_substance_with_concentration(self):
        """Test dose substance parsing with concentration"""
        test_cases = [
            ("Heparin 1000u/ml", "Heparin", Decimal("1000"), "u/ml"),
            ("Heparin 1000U/mL", "Heparin", Decimal("1000"), "u/ml"),
            ("Dox diet (200 mg/kg)", "Dox", Decimal("200"), "mg/kg"),
            ("Heparin (1000U/mL)", "Heparin", Decimal("1000"), "u/ml"),
        ]

        for (
            input_str,
            expected_name,
            expected_conc,
            expected_unit,
        ) in test_cases:
            with self.subTest(input=input_str):
                result = self.blank_model._parse_dose_sub_to_nonviral_material(
                    input_str
                )
                self.assertEqual(result.name, expected_name)
                self.assertEqual(result.concentration, expected_conc)
                self.assertEqual(result.concentration_unit, expected_unit)

    def test_parse_dose_substance_without_concentration(self):
        """Test dose substance parsing without concentration"""
        result = self.blank_model._parse_dose_sub_to_nonviral_material(
            "2% Evans blue"
        )
        self.assertEqual(result.name, "2% Evans blue")
        self.assertIsNone(result.concentration)
        self.assertIsNone(result.concentration_unit)

    def test_parse_dose_substance_invalid(self):
        """Test dose substance parsing with invalid inputs"""
        # Too long string
        long_string = "heparin  1000U/mL (2 mice only)"
        result = self.blank_model._parse_dose_sub_to_nonviral_material(
            long_string
        )
        self.assertIsNone(result)

        # None
        result_none = self.blank_model._parse_dose_sub_to_nonviral_material(
            None
        )
        self.assertIsNone(result_none)

    def test_parse_iacuc_protocol(self):
        """Test IACUC protocol parsing"""
        self.assertEqual(
            self.blank_model._parse_iacuc_protocol(
                "2212 - Investigating Brain States"
            ),
            "2212",
        )
        self.assertEqual(
            self.blank_model._parse_iacuc_protocol("2115"), "2115"
        )
        self.assertIsNone(
            self.blank_model._parse_iacuc_protocol("Invalid Protocol")
        )

    def test_parse_titer_scientific_notation(self):
        """Test titer parsing with scientific notation"""
        test_cases = [
            ("1e12", 1000000000000, "gc/mL"),
            ("1.5e13", 15000000000000, "gc/mL"),
            ("2E10", 20000000000, "gc/mL"),
        ]

        for input_str, expected_value, expected_unit in test_cases:
            with self.subTest(input=input_str):
                value, unit = self.blank_model._parse_titer(input_str)
                self.assertEqual(value, expected_value)
                self.assertEqual(unit, expected_unit)

    def test_parse_titer_with_unit(self):
        """Test titer parsing with unit"""
        test_cases = [
            ("1000000 gc/mL", 1000000, "gc/mL"),
            ("500000 vg/mL", 500000, "vg/mL"),
        ]

        for input_str, expected_value, expected_unit in test_cases:
            with self.subTest(input=input_str):
                value, unit = self.blank_model._parse_titer(input_str)
                self.assertEqual(value, expected_value)
                self.assertEqual(unit, expected_unit)

    def test_parse_titer_none(self):
        """Test titer parsing with None"""
        value, unit = self.blank_model._parse_titer(None)
        self.assertIsNone(value)
        self.assertEqual(unit, "gc/mL")

    def test_map_time_unit(self):
        """Test time unit mapping"""
        test_cases = [
            ("s", TimeUnit.S),
            ("sec", TimeUnit.S),
            ("second", TimeUnit.S),
            ("min", TimeUnit.M),
            ("minutes", TimeUnit.M),
            ("hr", TimeUnit.HR),
            ("hour", TimeUnit.HR),
        ]

        for input_str, expected_unit in test_cases:
            with self.subTest(input=input_str):
                result = self.blank_model._map_time_unit(input_str)
                self.assertEqual(result, expected_unit)

    def test_is_scientific_notation(self):
        """Test scientific notation detection"""
        self.assertTrue(self.blank_model._is_scientific_notation("1e12"))
        self.assertTrue(self.blank_model._is_scientific_notation("1.5E13"))
        self.assertTrue(self.blank_model._is_scientific_notation("2e+10"))
        self.assertFalse(self.blank_model._is_scientific_notation("1000"))
        self.assertFalse(self.blank_model._is_scientific_notation("abc"))

    def test_is_value_with_unit(self):
        """Test value with unit detection"""
        self.assertTrue(self.blank_model._is_value_with_unit("70.4 uL"))
        self.assertTrue(self.blank_model._is_value_with_unit("30 s"))
        self.assertTrue(self.blank_model._is_value_with_unit("1000 gc/mL"))
        self.assertFalse(self.blank_model._is_value_with_unit("1000"))
        self.assertFalse(self.blank_model._is_value_with_unit("abc"))


if __name__ == "__main__":
    unittest_main()
