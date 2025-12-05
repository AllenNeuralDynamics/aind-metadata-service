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
        test_none_data = {"FileSystemObjectType": 0, "Id": 1}
        las_model = Las2020List.model_validate(test_none_data)
        mapper = MappedLASList(las=las_model)
        self.assertIsNone(mapper.aind_protocol)

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
        none_test_data = deepcopy(self.ip_injection_data)
        none_test_data["dosevolume"] = None
        none_las_model = Las2020List.model_validate(none_test_data)
        none_mapper = MappedLASList(las=none_las_model)
        self.assertIsNone(none_mapper.aind_dosevolume)

        self.assertEqual(self.mapper.aind_dosevolume, Decimal("70.4"))


    def test_map_dose_duration(self):
        """Test dose duration mapping"""
        none_test_data = deepcopy(self.ip_injection_data)
        none_test_data["doseduration"] = None
        none_las_model = Las2020List.model_validate(none_test_data)
        none_mapper = MappedLASList(las=none_las_model)
        self.assertIsNone(none_mapper.aind_doseduration)
        self.assertIsNone(none_mapper.aind_doseduration_unit)

        decimal_str_data = deepcopy(self.ip_injection_data)
        decimal_str_data["doseduration"] = "30.0"
        decimal_str_las_model = Las2020List.model_validate(decimal_str_data)
        decimal_str_mapper = MappedLASList(las=decimal_str_las_model)
        self.assertEqual(decimal_str_mapper.aind_doseduration, 30.0)

        no_unit_data = deepcopy(self.ip_injection_data)
        no_unit_data["doseduration"] = "30"  # No unit
        no_unit_las_model = Las2020List.model_validate(no_unit_data)
        no_unit_mapper = MappedLASList(las=no_unit_las_model)
        self.assertEqual(no_unit_mapper.aind_doseduration, 30)
        self.assertIsNone(no_unit_mapper.aind_doseduration_unit)

        self.assertEqual(self.mapper.aind_doseduration, 30)
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

class TestLAS2020InjectableMaterialsMapping(TestCase):
    """Tests _map_injectable_materials method with systematic field coverage"""

    def test_map_injectable_materials_all_fields_all_suffixes(self):
        """Test all material numbers (1-5) with all suffixes ('', 'b', 'c', 'd') systematically"""
        field_types = ['Sub', 'Lot', 'GC', 'Tite', 'VolV']
        suffixes = ['', 'b', 'c', 'd']
        
        for material_num in range(1, 6):
            with self.subTest(material_num=material_num):
                # Build test data with all fields for this material number and all suffixes
                test_data = {
                    "FileSystemObjectType": 0,
                    "Id": material_num,
                }
                
                # Add all field combinations for all suffixes
                for suffix in suffixes:
                    suffix_label = suffix if suffix else "no_suffix"
                    test_data[f"roSub{material_num}{suffix}"] = f"AAV-{material_num}{suffix_label}"
                    test_data[f"roLot{material_num}{suffix}"] = f"LOT-{material_num}{suffix_label}"
                    test_data[f"roGC{material_num}{suffix}"] = f"{material_num}e13"
                    test_data[f"roTite{material_num}{suffix}"] = f"{material_num}e12"
                    test_data[f"roVolV{material_num}{suffix}"] = f"{material_num * 100}"
                
                las_model = Las2020List.model_validate(test_data)
                mapper = MappedLASList(las=las_model)
                
                materials = mapper._map_injectable_materials(material_num=material_num)
                
                # Should have 4 materials (one for each suffix)
                self.assertEqual(len(materials), 4)
                
                # Verify each material has correct data
                for idx, suffix in enumerate(suffixes):
                    suffix_label = suffix if suffix else "no_suffix"
                    with self.subTest(suffix=suffix):
                        self.assertEqual(materials[idx].substance, f"AAV-{material_num}{suffix_label}")
                        self.assertEqual(materials[idx].prep_lot_id, f"LOT-{material_num}{suffix_label}")
                        self.assertEqual(materials[idx].genome_copy, f"{material_num}e13")
                        self.assertEqual(materials[idx].titer, f"{material_num}e12")
                        self.assertEqual(materials[idx].virus_volume, Decimal(str(material_num * 100)))

    def test_map_injectable_materials_property_mappings(self):
        """Test that all aind_ro_* properties correctly map to _las fields"""
        material_nums = range(1, 6)
        suffixes = ['', 'b', 'c', 'd']
        
        for material_num in material_nums:
            for suffix in suffixes:
                with self.subTest(material_num=material_num, suffix=suffix):
                    test_data = {
                        "FileSystemObjectType": 0,
                        "Id": 100 + material_num,
                    }
                    
                    # Set raw LAS field values
                    test_values = {
                        'Sub': f"Test-Sub-{material_num}{suffix}",
                        'Lot': f"Test-Lot-{material_num}{suffix}",
                        'GC': f"Test-GC-{material_num}{suffix}",
                        'Tite': f"Test-Tite-{material_num}{suffix}",
                        'VolV': f"{material_num}{len(suffix)}",  # unique numeric value
                    }
                    
                    for field_key, field_value in test_values.items():
                        # Construct LAS field name: roSub1, roLot1b, roVol_v1c, etc.
                        las_field = f"ro{field_key}{material_num}{suffix}"
                        test_data[las_field] = field_value
                    
                    las_model = Las2020List.model_validate(test_data)
                    mapper = MappedLASList(las=las_model)
                    
                    # Check property mappings
                    for field_key in test_values.keys():
                        # Property name matches field_key but lowercase
                        aind_property = f"aind_ro_{field_key.lower()}{material_num}{suffix}"
                        
                        if hasattr(mapper, aind_property):
                            actual_value = getattr(mapper, aind_property)
                            expected_value = test_values[field_key]
                            self.assertEqual(actual_value, expected_value,
                                f"Property {aind_property} mismatch")

    def test_map_injectable_materials_sparse_data(self):
        """Test with sparse data - random combinations of fields present"""
        import random
        
        suffixes = ['', 'b', 'c', 'd']
        
        for material_num in range(1, 6):
            with self.subTest(material_num=material_num):
                test_data = {
                    "FileSystemObjectType": 0,
                    "Id": 200 + material_num,
                }
                
                # Randomly decide which suffixes to include (at least one)
                included_suffixes = random.sample(suffixes, k=random.randint(1, 4))
                
                expected_material_count = 0
                for suffix in included_suffixes:
                    # Always include Sub (required for material to be created)
                    test_data[f"roSub{material_num}{suffix}"] = f"AAV-{material_num}{suffix}"
                    expected_material_count += 1
                    
                    # Randomly include other fields
                    if random.choice([True, False]):
                        test_data[f"roLot{material_num}{suffix}"] = f"LOT-{material_num}{suffix}"
                    if random.choice([True, False]):
                        test_data[f"roGC{material_num}{suffix}"] = f"{material_num}e13"
                    if random.choice([True, False]):
                        test_data[f"roTite{material_num}{suffix}"] = f"{material_num}e12"
                    if random.choice([True, False]):
                        test_data[f"roVolV{material_num}{suffix}"] = f"{material_num * 50}"
                
                las_model = Las2020List.model_validate(test_data)
                mapper = MappedLASList(las=las_model)
                
                materials = mapper._map_injectable_materials(material_num=material_num)
                
                self.assertEqual(len(materials), expected_material_count,
                    f"Expected {expected_material_count} materials for included suffixes {included_suffixes}")
                
                # Verify all materials have substance (required field)
                for material in materials:
                    self.assertIsNotNone(material.substance)

    def test_map_injectable_materials_complete_coverage_matrix(self):
        """Generate a coverage matrix testing every field exists and maps correctly"""
        material_nums = range(1, 6)
        suffixes = ['', 'b', 'c', 'd']
        fields = ['Sub', 'Lot', 'GC', 'Tite', 'Vol_v']  # Changed from 'VolV' to 'Vol_v'

        # Test that every combination can be accessed
        for material_num in material_nums:
            for suffix in suffixes:
                for field in fields:
                    with self.subTest(material_num=material_num, suffix=suffix, field=field):
                        test_data = {
                            "FileSystemObjectType": 0,
                            "Id": 300,
                        }

                        las_field = f"ro{field}{material_num}{suffix}"
                        test_value = f"test_{field}_{material_num}_{suffix}" if field != 'Vol_v' else "123.45"
                        test_data[las_field] = test_value

                        # Must have Sub for material to be created
                        if field != 'Sub':
                            test_data[f"roSub{material_num}{suffix}"] = "AAV-Test"

                        las_model = Las2020List.model_validate(test_data)
                        mapper = MappedLASList(las=las_model)

                        # Verify property exists and is accessible
                        aind_property = f"aind_ro_{field.lower()}{material_num}{suffix}"
                        self.assertTrue(hasattr(mapper, aind_property),
                            f"Property {aind_property} does not exist")

                        # Verify through _map_injectable_materials
                        materials = mapper._map_injectable_materials(material_num=material_num)
                        self.assertEqual(len(materials), 1)

    def test_map_injectable_materials_only_substance_all_combinations(self):
        """Test that material is created with only substance for all combinations"""
        for material_num in range(1, 6):
            for suffix in ['', 'b', 'c', 'd']:
                with self.subTest(material_num=material_num, suffix=suffix):
                    test_data = {
                        "FileSystemObjectType": 0,
                        "Id": 400 + material_num,
                        f"roSub{material_num}{suffix}": f"AAV-Only-{material_num}{suffix}",
                    }
                    
                    las_model = Las2020List.model_validate(test_data)
                    mapper = MappedLASList(las=las_model)
                    
                    materials = mapper._map_injectable_materials(material_num=material_num)
                    
                    self.assertEqual(len(materials), 1)
                    self.assertEqual(materials[0].substance, f"AAV-Only-{material_num}{suffix}")
                    self.assertIsNone(materials[0].prep_lot_id)
                    self.assertIsNone(materials[0].genome_copy)
                    self.assertIsNone(materials[0].titer)
                    self.assertIsNone(materials[0].virus_volume)

    def test_map_injectable_materials_no_materials_all_numbers(self):
        """Test that no materials are created when substance is missing for all material numbers"""
        for material_num in range(1, 6):
            with self.subTest(material_num=material_num):
                test_data = {
                    "FileSystemObjectType": 0,
                    "Id": 500 + material_num,
                    # No roSub fields - materials shouldn't be created
                    f"roLot{material_num}": "LOT-NoSub",
                    f"roGC{material_num}": "1e13",
                }
                
                las_model = Las2020List.model_validate(test_data)
                mapper = MappedLASList(las=las_model)
                
                materials = mapper._map_injectable_materials(material_num=material_num)
                
                self.assertEqual(len(materials), 0)

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

    def test_get_surgery_author_lookup_id(self):
        """Test basic surgery creation"""
        test_data = deepcopy(self.full_surgery_data)
        test_data["AuthorId"] = None
        test_data["AuthorLookupId"] = 6000
        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)
        surgery = mapper.get_surgery(subject_id="000000")
        self.assertIsInstance(surgery, Surgery)
        self.assertIsNotNone(surgery.experimenters)
        self.assertEqual(surgery.experimenters[0], "LAS-6000")
        self.assertEqual(surgery.ethics_review_id, "2212")

    def test_get_surgery_validation_error(self):
        """Test surgery creation with missing start_date (required field)"""
        test_data = deepcopy(self.full_surgery_data)
        test_data["nStart_x0020_Date"] = None
        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)
        
        surgery = mapper.get_surgery(subject_id="000000")

        self.assertIsNotNone(surgery)
        self.assertIsNone(surgery.start_date)

    def test_get_surgery_ip_injection_validation_error_no_volume_or_current(self):
        """Test IP injection when InjectionDynamics validation fails (no volume or current)"""
        test_data = {
            "FileSystemObjectType": 0,
            "Id": 100,
            "AuthorId": 5358,
            "Protocol": "2207 - In Vitro Brain Stimulation",
            "nStart_x0020_Date": "2024-06-21T07:00:00Z",
            "ReqPro1": "Dosing",
            "doseRoute": "Intraperitoneal (IP)",
            "doseSub": "Heparin 1000U/mL",
        }
        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)
        
        surgery = mapper.get_surgery(subject_id="000000")

        self.assertIsNotNone(surgery)
        self.assertEqual(len(surgery.procedures), 1)
        ip_injection = surgery.procedures[0]
        self.assertIsNone(ip_injection.dynamics[0].volume)

    def test_get_surgery_ro_injection_validation_error_no_volume_or_current(self):
        """Test RO injection when InjectionDynamics validation fails"""
        test_data = {
            "FileSystemObjectType": 0,
            "Id": 101,
            "AuthorId": 5358,
            "Protocol": "2212 - Investigating Brain States",
            "nStart_x0020_Date": "2024-06-21T07:00:00Z",
            "ReqPro1": "Retro-Orbital Injection",
            "nROID1": "123456",
            "roEye1": "Behind Right",
            # Missing roVol1 - will cause validation error
            "roSub1": "AAV-Test",
        }
        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)
        
        surgery = mapper.get_surgery(subject_id="123456")
        
        # Should still create surgery using model_construct
        self.assertIsNotNone(surgery)
        self.assertEqual(len(surgery.procedures), 1)
        ro_injection = surgery.procedures[0]
        self.assertIsNone(ro_injection.dynamics[0].volume)

    def test_get_surgery_injection_validation_error_empty_materials(self):
        """Test injection with empty injection_materials (min_length=1 requirement)"""
        test_data = {
            "FileSystemObjectType": 0,
            "Id": 102,
            "AuthorId": 5358,
            "Protocol": "2212 - Investigating Brain States",
            "nStart_x0020_Date": "2024-06-21T07:00:00Z",
            "ReqPro1": "Retro-Orbital Injection",
            "nROID1": "123456",
            "roEye1": "Behind Right",
            "roVol1": "100",
            # roSub1 missing - no materials will be mapped
        }
        las_model = Las2020List.model_validate(test_data)
        mapper = MappedLASList(las=las_model)
        
        surgery = mapper.get_surgery(subject_id="123456")
        
        # Should create surgery, but with empty injection_materials list
        self.assertIsNotNone(surgery)
        self.assertEqual(len(surgery.procedures), 1)
        ro_injection = surgery.procedures[0]
        self.assertEqual(len(ro_injection.injection_materials), 0)

    # def test_get_surgery_mixed_valid_and_invalid_procedures(self):
    #     """Test surgery with one valid and one invalid procedure"""
    #     test_data = {
    #         "FileSystemObjectType": 0,
    #         "Id": 103,
    #         "AuthorId": 5358,
    #         "Protocol": "2212 - Test",
    #         "nStart_x0020_Date": "2024-06-21T07:00:00Z",
    #         "ReqPro1": "Dosing",
    #         "ReqPro2": "Retro-Orbital Injection",
    #         "doseRoute": "Intraperitoneal (IP)",
    #         "doseSub": "Heparin 1000U/mL",
    #         "dosevolume": "70.4",
    #         "doseduration": "30 s",
    #         # RO injection has issues
    #         "nROID1": "123456",
    #         "roEye1": "Behind Right",
    #         # Missing roVol1 - RO will have validation error
    #         "roSub1": "AAV-Test",
    #     }
    #     las_model = Las2020List.model_validate(test_data)
    #     mapper = MappedLASList(las=las_model)
    #
    #     surgery = mapper.get_surgery(subject_id="123456")
    #
    #     # Should create surgery with both procedures
    #     self.assertIsNotNone(surgery)
    #     self.assertEqual(len(surgery.procedures), 2)
    #
    #     # First procedure (IP) should be valid
    #     ip_injection = surgery.procedures[0]
    #     self.assertEqual(ip_injection.targeted_structure, InjectionTargets.INTRAPERITONEAL)
    #     self.assertIsNotNone(ip_injection.dynamics[0].volume)
    #
    #     # Second procedure (RO) should be created with model_construct
    #     ro_injection = surgery.procedures[1]
    #     self.assertEqual(ro_injection.targeted_structure, InjectionTargets.RETRO_ORBITAL)
    #     self.assertIsNone(ro_injection.dynamics[0].volume)
    #
    # def test_get_surgery_ro_injection_validation_error_multiple_materials(self):
    #     """Test RO injection with multiple materials where some cause validation errors"""
    #     test_data = {
    #         "FileSystemObjectType": 0,
    #         "Id": 104,
    #         "AuthorId": 5358,
    #         "Protocol": "2212 - Test",
    #         "nStart_x0020_Date": "2024-06-21T07:00:00Z",
    #         "ReqPro1": "Retro-Orbital Injection",
    #         "nROID1": "123456",
    #         "roEye1": "Behind Right",
    #         "roVol1": "100",
    #         "roSub1": "AAV-Valid",
    #         "roLot1": "LOT123",
    #         "roSub1b": "AAV-Also-Valid",
    #         "roLot1b": "LOT456",
    #     }
    #     las_model = Las2020List.model_validate(test_data)
    #     mapper = MappedLASList(las=las_model)
    #
    #     surgery = mapper.get_surgery(subject_id="123456")
    #
    #     # Should create surgery with 2 viral materials
    #     self.assertIsNotNone(surgery)
    #     self.assertEqual(len(surgery.procedures), 1)
    #     ro_injection = surgery.procedures[0]
    #     self.assertEqual(len(ro_injection.injection_materials), 2)
    #
    # def test_get_surgery_validation_error_all_fields_missing(self):
    #     """Test surgery creation with minimal data causing multiple validation errors"""
    #     test_data = {
    #         "FileSystemObjectType": 0,
    #         "Id": 105,
    #         "ReqPro1": "Retro-Orbital Injection",
    #         "nROID1": "123456",
    #     }
    #     las_model = Las2020List.model_validate(test_data)
    #     mapper = MappedLASList(las=las_model)
    #
    #     surgery = mapper.get_surgery(subject_id="123456")
    #
    #     # Should create surgery using model_construct with many None fields
    #     self.assertIsNotNone(surgery)
    #     self.assertIsNone(surgery.ethics_review_id)
    #     self.assertIsNone(surgery.start_date)
    #     self.assertEqual(surgery.experimenters, [None])
    #
    #     # Procedure should have empty materials
    #     self.assertEqual(len(surgery.procedures), 1)
    #     self.assertEqual(len(surgery.procedures[0].injection_materials), 0)

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

    def test_parse_titer_str_all_cases(self):
        """Test _parse_titer_str with all input variations"""
        test_cases = [
            # (input, expected_output, description)
            ("12345", 12345, "plain integer"),
            ("+678", 678, "integer with positive sign"),
            ("-999", -999, "integer with negative sign"),
            ("0", 0, "zero"),
            ("123.45", None, "decimal (doesn't match INTEGER_REGEX)"),
            ("1e10", None, "scientific notation (doesn't match INTEGER_REGEX)"),
            ("abc", None, "text"),
            ("", None, "empty string"),
        ]

        for input_str, expected, description in test_cases:
            with self.subTest(input=input_str, case=description):
                result = self.blank_model._parse_titer_str(input_str)
                self.assertEqual(result, expected)

    def test_parse_titer_all_cases(self):
        """Test _parse_titer with all input formats and edge cases"""
        test_cases = [
            # (input, expected_value, expected_unit, description)
            # None case
            (None, None, "gc/mL", "None input returns None with default unit"),
            
            # Plain integer (via _parse_titer_str path)
            ("12345", 12345, "gc/mL", "plain integer"),
            ("  12345  ", 12345, "gc/mL", "integer with whitespace"),
            ("+789", 789, "gc/mL", "integer with positive sign"),
            ("-456", -456, "gc/mL", "integer with negative sign"),
            ("0", 0, "gc/mL", "zero"),
            
            # Scientific notation path
            ("1e12", 1000000000000, "gc/mL", "scientific notation lowercase e"),
            ("1.5e13", 15000000000000, "gc/mL", "scientific notation with decimal"),
            ("2E10", 20000000000, "gc/mL", "scientific notation uppercase E"),
            ("1.5e-3", 0, "gc/mL", "scientific notation negative exponent"),
            
            # Value with unit path
            ("1000000 gc/mL", 1000000, "gc/mL", "value with gc/mL unit"),
            ("500000 vg/mL", 500000, "vg/mL", "value with vg/mL unit"),
            ("12345gc/mL", 12345, "gc/mL", "value with unit no space"),
            ("12345   gc/mL", 12345, "gc/mL", "value with unit multiple spaces"),
            
            # Unparseable cases (final fallback)
            ("unknown", None, "gc/mL", "unparseable text"),
            ("abc123def", None, "gc/mL", "mixed text and numbers"),
            ("", None, "gc/mL", "empty string after strip"),
            ("123.45", None, "gc/mL", "decimal without unit"),
        ]
        
        for input_str, expected_value, expected_unit, description in test_cases:
            with self.subTest(input=input_str, case=description):
                value, unit = self.blank_model._parse_titer(input_str)
                self.assertEqual(value, expected_value, f"Value mismatch for {description}")
                self.assertEqual(unit, expected_unit, f"Unit mismatch for {description}")


if __name__ == "__main__":
    unittest_main()
