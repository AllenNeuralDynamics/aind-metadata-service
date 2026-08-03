"""Tests ExaSPIM Procedures mapper"""

import os
from datetime import date, timedelta
from pathlib import Path
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.components.injection_procedures import (
    Injection,
    InjectionDynamics,
    InjectionProfile,
    ViralMaterial,
)
from aind_data_schema.components.reagent import (
    ProbeReagent,
    Solution,
)
from aind_data_schema.components.specimen_procedures import SpecimenProcedure
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema.core.procedures import Procedures
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.registries import Registry
from aind_data_schema_models.species import Species
from aind_data_schema_models.specimen_procedure_types import (
    SpecimenProcedureType,
)
from aind_data_schema_models.units import VolumeUnit
from aind_smartsheet_service_async_client.models import (
    ExaSPIMInfo,
    ImagingQueue,
    MouseTracker,
    QcSheet,
    SampleTracking,
)

from aind_metadata_service_server.mappers.exaspim_procedures import (
    ExaspimProceduresMapper,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."


class TestExaspimBasicParsing(TestCase):
    """Tests basic parsing utilities"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.mapper = ExaspimProceduresMapper()

    def test_parse_date_various_formats(self):
        """Test date parsing with different formats"""
        result1 = self.mapper._parse_date("07/20/23")
        self.assertEqual(result1, date(2023, 7, 20))

        result2 = self.mapper._parse_date("12/14/2023")
        self.assertEqual(result2, date(2023, 12, 14))

        result3 = self.mapper._parse_date("2023-03-31")
        self.assertEqual(result3, date(2023, 3, 31))

        result4 = self.mapper._parse_date("2023-01-08T00:00:00Z")
        self.assertEqual(result4, date(2023, 1, 8))

        self.assertIsNone(self.mapper._parse_date(None))
        self.assertIsNone(self.mapper._parse_date(""))
        self.assertIsNone(self.mapper._parse_date("  "))

    def test_parse_date_already_date_object(self):
        """Test parsing when input is already a date"""
        test_date = date(2023, 5, 5)
        result = self.mapper._parse_date(test_date)
        self.assertEqual(result, test_date)

    def test_is_numeric(self):
        """Test numeric value detection"""
        self.assertTrue(self.mapper._is_numeric(100))
        self.assertTrue(self.mapper._is_numeric(3.14))
        self.assertTrue(self.mapper._is_numeric("500.2"))
        self.assertTrue(self.mapper._is_numeric("1.35E+14"))

        self.assertFalse(self.mapper._is_numeric(None))
        self.assertFalse(self.mapper._is_numeric("n/a"))
        self.assertFalse(self.mapper._is_numeric(""))
        self.assertFalse(self.mapper._is_numeric("text"))

    def test_parse_experimenters_single(self):
        """Test parsing single experimenter"""
        sample_tracking = SampleTracking.model_construct(
            processing_lead="Rajvi Javeri"
        )
        result = self.mapper._parse_experimenters(sample_tracking)
        self.assertEqual(result, ["Rajvi Javeri"])

    def test_parse_experimenters_multiple_comma(self):
        """Test parsing multiple experimenters with comma"""
        sample_tracking = SampleTracking.model_construct(
            processing_lead="Alice Smith, Bob Jones"
        )
        result = self.mapper._parse_experimenters(sample_tracking)
        self.assertEqual(result, ["Alice Smith", "Bob Jones"])

    def test_parse_experimenters_multiple_semicolon(self):
        """Test parsing multiple experimenters with semicolon"""
        sample_tracking = SampleTracking.model_construct(
            processing_lead="Alice Smith; Bob Jones; Charlie Brown"
        )
        result = self.mapper._parse_experimenters(sample_tracking)
        self.assertEqual(result, ["Alice Smith", "Bob Jones", "Charlie Brown"])

    def test_parse_experimenters_empty(self):
        """Test parsing empty or None experimenters"""
        sample_tracking_none = SampleTracking.model_construct(
            processing_lead=None
        )
        self.assertEqual(
            self.mapper._parse_experimenters(sample_tracking_none), []
        )

        sample_tracking_empty = SampleTracking.model_construct(
            processing_lead=""
        )
        self.assertEqual(
            self.mapper._parse_experimenters(sample_tracking_empty), []
        )

    def test_parse_experimenters_whitespace_only(self):
        """Test parsing whitespace-only experimenters"""
        sample_tracking = SampleTracking.model_construct(processing_lead="   ")
        self.assertEqual(self.mapper._parse_experimenters(sample_tracking), [])


class TestExaspimAntibodyMapping(TestCase):
    """Tests antibody-related mapping functions"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.mapper = ExaspimProceduresMapper()

    def test_map_antibody_species(self):
        """Test antibody host species mapping"""
        test_cases = [
            ("Rabbit Anti-GFP", Species.EUROPEAN_RABBIT),
            ("Mouse IgG", Species.HOUSE_MOUSE),
            ("Rat Anti-tdT", Species.NORWAY_RAT),
            ("Goat Anti-tdT", Species.GOAT),
            ("Chicken IgY", Species.CHICKEN),
            ("Donkey anti-Rabbit", Species.DONKEY),
        ]

        for antibody_name, expected_species in test_cases:
            result = self.mapper._map_antibody_species(antibody_name)
            self.assertEqual(result, expected_species)

    def test_map_antibody_species_unknown(self):
        """Test antibody species for unknown host"""
        result = self.mapper._map_antibody_species("Unknown Anti-GFP")
        self.assertIsNone(result)

    def test_map_antibody_species_empty(self):
        """Test antibody species for empty string"""
        result = self.mapper._map_antibody_species("")
        self.assertIsNone(result)

    def test_map_antibody_source(self):
        """Test antibody source organization mapping"""
        test_cases = [
            ("gfp", Organization.ABCAM),
            ("GFP", Organization.ABCAM),
            ("tdtomato", Organization.SICGEN),
            ("Donkey anti-rabbit IgG (H+L) AF 488", Organization.INVITROGEN),
            ("Donkey anti-goat IgG (H+L) AF 568", Organization.INVITROGEN),
            ("Unknown antibody", Organization.OTHER),
        ]

        for antibody_name, expected_org in test_cases:
            result = self.mapper._map_antibody_source(antibody_name)
            self.assertEqual(result, expected_org)

    def test_map_rrid(self):
        """Test RRID mapping from catalog numbers"""
        rrid1 = self.mapper._map_rrid("AB290", "Rabbit Anti-GFP")
        self.assertIsNotNone(rrid1)
        self.assertEqual(rrid1.registry, Registry.RRID)
        self.assertEqual(rrid1.registry_identifier, "AB_303395")

        rrid2 = self.mapper._map_rrid("AB8181-200", "Goat Anti-tdT")
        self.assertIsNotNone(rrid2)
        self.assertEqual(rrid2.registry_identifier, "AB_2722750")

        rrid3 = self.mapper._map_rrid("A-21206", "Donkey anti-Rabbit")
        self.assertIsNotNone(rrid3)
        self.assertEqual(rrid3.registry_identifier, "AB_2535792")

        rrid4 = self.mapper._map_rrid("A-11057", "Donkey anti-Goat")
        self.assertIsNotNone(rrid4)
        self.assertEqual(rrid4.registry_identifier, "AB_2534104")

    def test_map_rrid_not_found(self):
        """Test RRID mapping for unknown catalog"""
        result = self.mapper._map_rrid("UNKNOWN123", "Some Antibody")
        self.assertIsNone(result)

    def test_map_rrid_empty(self):
        """Test RRID mapping for empty catalog"""
        result = self.mapper._map_rrid("", "Some Antibody")
        self.assertIsNone(result)

    def test_map_primary_antibody_target(self):
        """Test primary antibody protein target mapping"""
        test_cases = [
            ("Anti-GFP", "Green Fluorescent Protein"),
            ("Rabbit Anti-GFP", "Green Fluorescent Protein"),
            ("Anti-tdTomato", "tdTomato"),
            ("Goat Anti-tdt", "tdTomato"),
            ("Anti-mTFP", "monomeric Teal Fluorescent Protein 1"),
        ]

        for antibody_name, expected_target in test_cases:
            result = self.mapper._map_primary_antibody_target(antibody_name)
            self.assertEqual(result, expected_target)

    def test_map_secondary_antibody_target(self):
        """Test secondary antibody target mapping"""
        result1 = self.mapper._map_secondary_antibody_target(
            "Donkey anti-Rabbit IgG", "Rabbit Anti-GFP"
        )
        self.assertEqual(result1, "Rabbit antibody")

        result2 = self.mapper._map_secondary_antibody_target(
            "Donkey anti-Goat IgG", "Goat Anti-tdT"
        )
        self.assertEqual(result2, "Goat antibody")

        result3 = self.mapper._map_secondary_antibody_target(
            "Donkey anti-Mouse IgG", "Some Unknown Primary"
        )
        self.assertEqual(result3, "Mouse antibody")


class TestExaspimTiterCalculation(TestCase):
    """Tests viral titer calculation"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.mapper = ExaspimProceduresMapper()

    def test_get_titer_effective(self):
        """Test titer priority: effective titer first (virus2+)"""
        data = {
            "num": 1,
            "virus2_effective_titer_gc_ml": "1.0E+12",
            "virus2_working_titer_gc_ml": "5.0E+11",
            "virus2_stock_titer_gc_ml": "2.0E+11",
        }
        mouse_tracker = MouseTracker.model_validate(data)
        result = self.mapper._get_titer_for_virus(mouse_tracker, 2)
        self.assertEqual(result, "1.0E+12")

    def test_get_titer_working(self):
        """Test titer priority: working titer when no effective (virus1)"""
        data = {
            "num": 1,
            "working_titer_gc_ml": "5.0E+11",
            "virus1_stock_titer_gc_ml": "2.0E+11",
        }
        mouse_tracker = MouseTracker.model_validate(data)
        result = self.mapper._get_titer_for_virus(mouse_tracker, 1)
        self.assertEqual(result, "5.0E+11")

    def test_get_titer_stock_with_dose_present(self):
        """Test titer uses stock even when dose is present (no calculation)"""
        data = {
            "num": 1,
            "virus1_dose_gc": "1.0E+09",
            "virus1_stock_titer_gc_ml": "1.0E+11",
        }
        mouse_tracker = MouseTracker.model_validate(data)
        result = self.mapper._get_titer_for_virus(mouse_tracker, 1)
        self.assertEqual(result, "1.0E+11")

    def test_get_titer_priority_skips_dose(self):
        """Test titer priority completely skips dose field (virus2)"""
        data = {
            "num": 1,
            "virus2_dose_gc": "5.0E+11",
            "virus2_working_titer_gc_ml": "3.0E+11",
            "virus2_stock_titer_gc_ml": "1.0E+11",
        }
        mouse_tracker = MouseTracker.model_validate(data)
        result = self.mapper._get_titer_for_virus(mouse_tracker, 2)
        self.assertEqual(result, "3.0E+11")

    def test_get_titer_stock(self):
        """Test titer priority: stock titer as last resort"""
        data = {"num": 1, "virus1_stock_titer_gc_ml": "2.0E+11"}
        mouse_tracker = MouseTracker.model_validate(data)
        result = self.mapper._get_titer_for_virus(mouse_tracker, 1)
        self.assertEqual(result, "2.0E+11")

    def test_get_titer_none(self):
        """Test titer returns None when no data available"""
        data = {"num": 1}
        mouse_tracker = MouseTracker.model_validate(data)
        result = self.mapper._get_titer_for_virus(mouse_tracker, 1)
        self.assertIsNone(result)


class TestExaspimInjectionSurgery(TestCase):
    """Tests injection surgery building"""

    @classmethod
    def setUpClass(cls):
        """Set up test data from provided example"""
        cls.mouse_tracker_data = {
            "num": 1,
            "virus_mix_total_volume_injected_ro_ul": "100",
            "virus1_injection_date": "2023-03-31",
            "virus1": "Ef1a-fDOI-eGFP PHP.eB",
            "virus1_id": "VT1612g",
            "virus1_stock_titer_gc_ml": "1.35E+14",
            "virus1_dose_gc": "5.00E+11",
            "virus2_injection_date": "2023-03-31",
            "virus2": "CAG-FLEX-tdTom PHP.eB",
            "virus2_id": "v162851",
            "virus2_stock_titer_gc_ml": "1.90E+13",
            "virus2_dose_gc": "2.00E+10",
            "virus2_effective_titer_gc_ml": "200000000000",
        }
        cls.mouse_tracker = MouseTracker.model_validate(cls.mouse_tracker_data)
        cls.mapper = ExaspimProceduresMapper()

    def test_build_injection_surgery(self):
        """Test complete injection surgery building"""
        surgery = self.mapper.build_injection_surgery(self.mouse_tracker)

        self.assertIsNotNone(surgery)
        self.assertIsInstance(surgery, Surgery)
        self.assertEqual(surgery.start_date, date(2023, 3, 31))
        self.assertEqual(len(surgery.procedures), 2)

    def test_injection_materials(self):
        """Test injection materials are created correctly"""
        surgery = self.mapper.build_injection_surgery(self.mouse_tracker)

        injection1 = surgery.procedures[0]
        self.assertIsInstance(injection1, Injection)
        self.assertEqual(len(injection1.injection_materials), 1)

        material1 = injection1.injection_materials[0]
        self.assertIsInstance(material1, ViralMaterial)
        self.assertEqual(material1.name, "Ef1a-fDOI-eGFP PHP.eB")
        self.assertIsNotNone(material1.tars_identifiers)
        self.assertEqual(material1.tars_identifiers.virus_tars_id, "VT1612g")

    def test_injection_titer_priority(self):
        """Test titer uses correct priority (effective over stock)"""
        surgery = self.mapper.build_injection_surgery(self.mouse_tracker)

        injection2 = surgery.procedures[1]
        material2 = injection2.injection_materials[0]
        self.assertEqual(material2.titer, 200000000000)

    def test_injection_dynamics_ro_volume(self):
        """Test injection dynamics for RO injection"""
        surgery = self.mapper.build_injection_surgery(self.mouse_tracker)

        injection1 = surgery.procedures[0]
        self.assertEqual(len(injection1.dynamics), 1)

        dynamics = injection1.dynamics[0]
        self.assertIsInstance(dynamics, InjectionDynamics)
        self.assertEqual(dynamics.profile, InjectionProfile.BOLUS)
        self.assertEqual(dynamics.volume, 100000.0)
        self.assertEqual(dynamics.volume_unit, VolumeUnit.NL)

    def test_injection_surgery_no_viruses(self):
        """Test returns None when no viruses present"""
        empty_tracker = MouseTracker.model_validate({"num": 1})
        result = self.mapper.build_injection_surgery(empty_tracker)
        self.assertIsNone(result)

    def test_injection_surgery_stereotaxic_volume(self):
        """Test injection with stereotaxic volume"""
        tracker_data = {
            "num": 1,
            "virus1": "Test Virus",
            "virus1_injection_date": "2023-03-31",
            "virus1_stereotaxic_volume_injected_nl": "500",
            "virus1_stock_titer_gc_ml": "1.0E+12",
        }
        tracker = MouseTracker.model_validate(tracker_data)
        surgery = self.mapper.build_injection_surgery(tracker)

        self.assertIsNotNone(surgery)
        dynamics = surgery.procedures[0].dynamics[0]
        self.assertEqual(dynamics.volume, 500.0)
        self.assertEqual(dynamics.volume_unit, VolumeUnit.NL)

    def test_injection_surgery_virus4_stereotaxic_volume(self):
        """Test virus4 uses stereotaxic_volume_injected_nl field"""
        mouse_tracker = MouseTracker.model_construct(
            num=1,
            virus4="AAV-Test",
            virus4_id="V4-123",
            virus4_injection_date="2023-01-15",
            stereotaxic_volume_injected_nl="500",
            virus4_stock_titer_gc_ml="1E+12",
        )

        surgery = self.mapper.build_injection_surgery(mouse_tracker)
        self.assertIsNotNone(surgery)
        self.assertEqual(len(surgery.procedures), 1)
        self.assertEqual(surgery.procedures[0].dynamics[0].volume, 500.0)

    def test_injection_surgery_multiple_viruses(self):
        """Test injection surgery with multiple viruses"""
        mouse_tracker = MouseTracker.model_construct(
            num=1,
            virus1="AAV1-GFP",
            virus1_injection_date="2023-01-10",
            virus1_stereotaxic_volume_injected_nl="100",
            working_titer_gc_ml="1E+12",
            virus2="AAV2-tdTomato",
            virus2_injection_date="2023-01-11",
            virus2_stereotaxic_volume_injected_nl="200",
            virus2_effective_titer_gc_ml="2E+12",
        )

        surgery = self.mapper.build_injection_surgery(mouse_tracker)
        self.assertIsNotNone(surgery)
        self.assertEqual(len(surgery.procedures), 2)
        self.assertEqual(surgery.procedures[0].dynamics[0].volume, 100.0)
        self.assertEqual(surgery.procedures[1].dynamics[0].volume, 200.0)
        self.assertEqual(surgery.start_date, date(2023, 1, 10))

    def test_injection_surgery_no_volume_skips(self):
        """Test injections without volume data are skipped"""
        mouse_tracker = MouseTracker.model_construct(
            num=1,
            virus1="AAV1-GFP",
            working_titer_gc_ml="1E+12",
            virus2="AAV2-tdTomato",
            virus2_injection_date="2023-01-11",
            virus2_stereotaxic_volume_injected_nl="200",
            virus2_working_titer_gc_ml="2E+12",
        )

        surgery = self.mapper.build_injection_surgery(mouse_tracker)
        self.assertIsNotNone(surgery)
        self.assertEqual(len(surgery.procedures), 1)
        self.assertEqual(
            surgery.procedures[0].injection_materials[0].name, "AAV2-tdTomato"
        )

    def test_injection_surgery_zero_volume_skips(self):
        """Test zero volumes are skipped"""
        mouse_tracker = MouseTracker.model_construct(
            num=1,
            virus1="AAV1-GFP",
            virus1_stereotaxic_volume_injected_nl="0",
            working_titer_gc_ml="1E+12",
        )

        surgery = self.mapper.build_injection_surgery(mouse_tracker)
        self.assertIsNone(surgery)


class TestExaspimDelipidation(TestCase):
    """Tests delipidation procedure building"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.sample_tracking_data = {
            "sample": "671477",
            "processing_lead": "Rajvi Javeri",
            "dcm_delipidation_start": "2023-07-20",
            "dcm_delipidation_end": "2023-08-02",
            "sbip_delipidation_start": "2023-08-03",
            "sbip_delipidation_end": "2023-08-14",
        }
        cls.sample_tracking = SampleTracking.model_validate(
            cls.sample_tracking_data
        )
        cls.mapper = ExaspimProceduresMapper()

    def test_build_delipidation(self):
        """Test delipidation procedure creation"""
        result = self.mapper.build_delipidation(
            self.sample_tracking, "671477", ["Rajvi Javeri"]
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SpecimenProcedure)
        self.assertEqual(
            result.procedure_type, SpecimenProcedureType.DELIPIDATION
        )
        self.assertEqual(result.specimen_id, "671477")
        self.assertEqual(result.start_date, date(2023, 7, 20))
        self.assertEqual(result.end_date, date(2023, 8, 14))
        self.assertEqual(result.experimenters, ["Rajvi Javeri"])

    def test_delipidation_reagents(self):
        """Test delipidation includes correct reagents"""
        result = self.mapper.build_delipidation(
            self.sample_tracking, "671477", []
        )

        self.assertEqual(len(result.procedure_details), 2)
        reagent_names = [r.name for r in result.procedure_details]
        self.assertIn("Dichloromethane (DCM)", reagent_names)
        self.assertIn(
            "SBiP (Sodium dodecylsulfate, Butanol, isoPropanol)",
            reagent_names,
        )

    def test_delipidation_missing_dates(self):
        """Test returns None when dates are missing"""
        incomplete_data = {"sample": "671477"}
        incomplete_tracking = SampleTracking.model_validate(incomplete_data)
        result = self.mapper.build_delipidation(
            incomplete_tracking, "671477", []
        )
        self.assertIsNone(result)


class TestExaspimImmunolabeling(TestCase):
    """Tests immunolabeling procedure building"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.sample_tracking_data = {
            "sample": "671477",
            "processing_lead": "Rajvi Javeri",
            "immuno_primary_ab_start_date": "2023-08-15",
            "immuno_secondary_ab_start_date": "2023-10-19",
            "immuno_primary_antibody1": "Goat Anti-tdT",
            "mass_of_primary_antibody1_used_per_brain_ug": "10",
            "primary_antibody1_catalog_num": "AB8181-200",
            "primary_antibody1_lot_num": "0081030221",
            "immuno_primary_antibody2": "Rabbit Anti-GFP",
            "mass_of_primary_antibody2_used_per_brain_ug": "10",
            "primary_antibody2_catalog_num": "AB290",
            "primary_antibody2_lot_num": "1037873-6",
            "immuno_secondary_antibody1": "Donkey anti-Goat IgG (H+L) AF 568",
            "mass_of_secondary_antibody1_used_per_brain_ug": "20",
            "secondary_antibody1_catalog_num": "A-11057",
            "secondary_antibody1_lot_num": "2304269",
            "immuno_secondary_antibody2": (
                "Donkey anti-Rabbit IgG (H+L) AF 488"
            ),
            "mass_of_secondary_antibody2_used_per_brain_ug": "20",
            "secondary_antibody2_catalog_num": "A-21206",
            "secondary_antibody2_lot_num": "2541645",
            "primary_antibody_rrid": "AB_2722750,",
            "secondary_antibody_rrid": "AB_2535794, AB_2534105",
        }
        cls.sample_tracking = SampleTracking.model_validate(
            cls.sample_tracking_data
        )
        cls.mapper = ExaspimProceduresMapper()

    def test_build_immunolabeling(self):
        """Test immunolabeling procedure creation"""
        result = self.mapper.build_immunolabeling(
            self.sample_tracking, "671477", ["Rajvi Javeri"]
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SpecimenProcedure)
        self.assertEqual(
            result.procedure_type, SpecimenProcedureType.IMMUNOLABELING
        )
        self.assertEqual(result.specimen_id, "671477")
        self.assertEqual(result.start_date, date(2023, 8, 15))
        self.assertEqual(result.end_date, date(2023, 10, 19))

    def test_immunolabeling_reagents_count(self):
        """Test correct number of antibody reagents"""
        result = self.mapper.build_immunolabeling(
            self.sample_tracking, "671477", []
        )

        self.assertEqual(len(result.procedure_details), 4)
        self.assertTrue(
            all(isinstance(r, ProbeReagent) for r in result.procedure_details)
        )

    def test_immunolabeling_primary_antibody_properties(self):
        """Test primary antibody properties"""
        result = self.mapper.build_immunolabeling(
            self.sample_tracking, "671477", []
        )

        primary1 = result.procedure_details[0]
        self.assertEqual(primary1.name, "Goat Anti-tdT")
        self.assertEqual(primary1.source, Organization.SICGEN)
        self.assertEqual(primary1.lot_number, "0081030221")
        self.assertIsNotNone(primary1.rrid)
        self.assertEqual(primary1.rrid.registry_identifier, "AB_2722750")
        self.assertEqual(primary1.target.mass, 10.0)

    def test_immunolabeling_secondary_antibody_properties(self):
        """Test secondary antibody properties"""
        result = self.mapper.build_immunolabeling(
            self.sample_tracking, "671477", []
        )

        secondary1 = result.procedure_details[2]
        self.assertEqual(secondary1.name, "Donkey anti-Goat IgG (H+L) AF 568")
        self.assertEqual(secondary1.source, Organization.INVITROGEN)
        self.assertEqual(secondary1.lot_number, "2304269")
        self.assertEqual(secondary1.target.mass, 20.0)
        self.assertIn("antibody", secondary1.target.protein.name.lower())

    def test_immunolabeling_notes_with_rrid(self):
        """Test notes include RRID information"""
        result = self.mapper.build_immunolabeling(
            self.sample_tracking, "671477", []
        )

        self.assertIsNotNone(result.notes)
        self.assertIn("Primary RRID:", result.notes)
        self.assertIn("Secondary RRID:", result.notes)

    def test_immunolabeling_missing_start_date(self):
        """Test returns None when start date is missing"""
        incomplete_data = {"sample": "671477"}
        incomplete_tracking = SampleTracking.model_validate(incomplete_data)
        result = self.mapper.build_immunolabeling(
            incomplete_tracking, "671477", []
        )
        self.assertIsNone(result)


class TestExaspimGelation(TestCase):
    """Tests gelation procedure building"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.sample_tracking_data = {
            "sample": "671477",
            "processing_lead": "Rajvi Javeri",
            "gelation_mbs_start": "2023-11-09",
            "gelation_mbs_end": "2023-11-13",
            "gelation_ac_x_start": "2023-11-13",
            "gelation_ac_x_end": "2023-11-17",
            "gelation_pbs_wash_start": "2023-11-17",
            "gelation_pbs_wash_end": "2023-11-21",
            "gelation_stock_xva_044_equilibration_start": "2023-11-21",
            "gelation_stock_xva_044_equilibration_end": "2023-11-28",
            "gelation_prok_rt_start": "2023-11-28",
            "gelation_prok_rt_end": "2023-12-03",
            "gelation_add_l_prok_37c_start": "2023-12-04",
            "gelation_add_l_prok_37c_end": "2023-12-10",
            "pbs_wash_start": "2023-12-11",
            "pbs_wash_end": "2023-12-14",
            "date_of_storage_in_pbs_az_0_05_4c": "12/14/23",
        }
        cls.sample_tracking = SampleTracking.model_validate(
            cls.sample_tracking_data
        )
        cls.mapper = ExaspimProceduresMapper()

    def test_build_gelation(self):
        """Test gelation procedure creation"""
        result = self.mapper.build_gelation(
            self.sample_tracking, "671477", ["Rajvi Javeri"]
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SpecimenProcedure)
        self.assertEqual(result.procedure_type, SpecimenProcedureType.GELATION)
        self.assertEqual(result.specimen_id, "671477")
        self.assertEqual(result.start_date, date(2023, 11, 9))
        self.assertEqual(result.end_date, date(2023, 12, 14))

    def test_gelation_reagents(self):
        """Test gelation includes correct reagents"""
        result = self.mapper.build_gelation(self.sample_tracking, "671477", [])

        self.assertEqual(len(result.procedure_details), 5)
        reagent_names = [r.name for r in result.procedure_details]
        self.assertIn(
            "MBS (m-Maleimidobenzoyl-N-hydroxysuccinimide ester)",
            reagent_names,
        )
        self.assertIn("Acryloyl-X (AcX)", reagent_names)
        self.assertIn("Stock X + VA-044", reagent_names)
        self.assertIn("Proteinase K (ProK)", reagent_names)
        self.assertIn("PBS", reagent_names)

    def test_gelation_protocol_parameters(self):
        """Test gelation protocol parameters include substep timing"""
        result = self.mapper.build_gelation(self.sample_tracking, "671477", [])

        self.assertIsNotNone(result.protocol_parameters)
        params = result.protocol_parameters
        self.assertIn("MBS Start", params)
        self.assertIn("MBS End", params)
        self.assertIn("AcX Start", params)
        self.assertIn("ProK RT Start", params)
        self.assertIn("4C Storage Date", params)

    def test_gelation_missing_start_date(self):
        """Test returns None when start date is missing"""
        incomplete_data = {"sample": "671477"}
        incomplete_tracking = SampleTracking.model_validate(incomplete_data)
        result = self.mapper.build_gelation(incomplete_tracking, "671477", [])
        self.assertIsNone(result)


class TestExaspimExpansion(TestCase):
    """Tests expansion procedure building"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.sample_tracking_data = {
            "sample": "671477",
            "status": "Imaged",
            "processing_lead": "Rajvi Javeri",
        }
        cls.sample_tracking = SampleTracking.model_validate(
            cls.sample_tracking_data
        )
        cls.mapper = ExaspimProceduresMapper()
        cls.imaging_start_date = date(2024, 1, 8)

    def test_build_expansion(self):
        """Test expansion procedure creation"""
        result = self.mapper.build_expansion(
            self.sample_tracking,
            "671477",
            self.imaging_start_date,
            ["Rajvi Javeri"],
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SpecimenProcedure)
        self.assertEqual(
            result.procedure_type, SpecimenProcedureType.EXPANSION
        )
        self.assertEqual(result.specimen_id, "671477")

    def test_expansion_dates_backtracked_from_imaging(self):
        """Test expansion dates are calculated by backtracking 3 days"""
        result = self.mapper.build_expansion(
            self.sample_tracking, "671477", self.imaging_start_date, []
        )

        expected_start = self.imaging_start_date - timedelta(days=3)
        self.assertEqual(result.start_date, expected_start)
        self.assertEqual(result.end_date, self.imaging_start_date)

    def test_expansion_reagents(self):
        """Test expansion includes correct reagents"""
        result = self.mapper.build_expansion(
            self.sample_tracking, "671477", self.imaging_start_date, []
        )

        self.assertEqual(len(result.procedure_details), 2)
        reagent_names = [r.name for r in result.procedure_details]
        self.assertIn("Saline-Sodium Citrate (SSC)", reagent_names)
        self.assertIn("Ascorbic Acid", reagent_names)

    def test_expansion_protocol_parameters(self):
        """Test expansion protocol parameters"""
        result = self.mapper.build_expansion(
            self.sample_tracking, "671477", self.imaging_start_date, []
        )

        params = result.protocol_parameters
        self.assertIn("ssc_duration", params)
        self.assertEqual(params["ssc_duration"], "2 days")
        self.assertIn("ascorbic_acid_duration", params)
        self.assertEqual(params["ascorbic_acid_duration"], "1 day")

    def test_expansion_not_imaged(self):
        """Test returns None when status is not 'Imaged'"""
        not_imaged_data = {"sample": "671477", "status": "Processing"}
        not_imaged_tracking = SampleTracking.model_validate(not_imaged_data)
        result = self.mapper.build_expansion(
            not_imaged_tracking, "671477", self.imaging_start_date, []
        )
        self.assertIsNone(result)

    def test_expansion_no_imaging_date(self):
        """Test returns None when imaging start date is missing"""
        result = self.mapper.build_expansion(
            self.sample_tracking, "671477", None, []
        )
        self.assertIsNone(result)


class TestExaspimMountingImaging(TestCase):
    """Tests mounting and imaging procedure building"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.imaging_queue_data = {
            "sample": "671477",
            "imaging_start_date": "2024-01-08",
            "imaging_end_date": "2024-01-10",
            "imaging_buffer": "0.05X SSC",
            "microscope": "ExaSPIM",
            "signal_channel_s": "488, 561",
            "notes": "First wider light sheet brain",
        }
        cls.imaging_queue = ImagingQueue.model_validate(cls.imaging_queue_data)
        cls.mapper = ExaspimProceduresMapper()

    def test_build_mounting_and_imaging(self):
        """Test mounting and imaging procedure creation"""
        result = self.mapper.build_mounting_and_imaging(
            self.imaging_queue, "671477", ["Rajvi Javeri"]
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SpecimenProcedure)
        self.assertEqual(result.procedure_type, SpecimenProcedureType.MOUNTING)
        self.assertEqual(result.specimen_id, "671477")
        self.assertEqual(result.start_date, date(2024, 1, 8))
        self.assertEqual(result.end_date, date(2024, 1, 10))

    def test_mounting_imaging_buffer_reagent(self):
        """Test imaging buffer is added as reagent"""
        result = self.mapper.build_mounting_and_imaging(
            self.imaging_queue, "671477", []
        )

        self.assertEqual(len(result.procedure_details), 1)
        buffer_reagent = result.procedure_details[0]
        self.assertIsInstance(buffer_reagent, Solution)
        self.assertIn("0.05X SSC", buffer_reagent.name)

    def test_mounting_notes_include_metadata(self):
        """Test notes include microscope, channels, and notes"""
        result = self.mapper.build_mounting_and_imaging(
            self.imaging_queue, "671477", []
        )

        self.assertIsNotNone(result.notes)
        self.assertIn("ExaSPIM", result.notes)
        self.assertIn("488, 561", result.notes)
        self.assertIn("First wider light sheet brain", result.notes)

    def test_mounting_missing_start_date(self):
        """Test returns None when start date is missing"""
        incomplete_data = {"sample": "671477"}
        incomplete_queue = ImagingQueue.model_validate(incomplete_data)
        result = self.mapper.build_mounting_and_imaging(
            incomplete_queue, "671477", []
        )
        self.assertIsNone(result)

    def test_mounting_default_end_date(self):
        """Test end date defaults to start date if missing"""
        data_no_end = {
            "sample": "671477",
            "imaging_start_date": "2024-01-08",
        }
        queue_no_end = ImagingQueue.model_validate(data_no_end)
        result = self.mapper.build_mounting_and_imaging(
            queue_no_end, "671477", []
        )

        self.assertEqual(result.start_date, result.end_date)


class TestExaspimFullIntegration(TestCase):
    """Tests complete procedures mapping integration"""

    @classmethod
    def setUpClass(cls):
        """Set up complete test data from provided example"""
        cls.exaspim_data = {
            "mouse_tracker_info": [
                {
                    "num": 1,
                    "sample_name": "Dbh-Cre; DAT-Flp",
                    "virus_mix_total_volume_injected_ro_ul": "100",
                    "virus1_injection_date": "2023-03-31",
                    "virus1": "Ef1a-fDOI-eGFP PHP.eB",
                    "virus1_id": "VT1612g",
                    "virus1_stock_titer_gc_ml": "1.35E+14",
                    "virus1_dose_gc": "5.00E+11",
                    "virus2_injection_date": "2023-03-31",
                    "virus2": "CAG-FLEX-tdTom PHP.eB",
                    "virus2_id": "v162851",
                    "virus2_effective_titer_gc_ml": "200000000000",
                }
            ],
            "sample_tracking_info": [
                {
                    "sample": "671477",
                    "processing_lead": "Rajvi Javeri",
                    "status": "Imaged",
                    "dcm_delipidation_start": "2023-07-20",
                    "sbip_delipidation_end": "2023-08-14",
                    "immuno_primary_ab_start_date": "2023-08-15",
                    "immuno_secondary_ab_start_date": "2023-10-19",
                    "immuno_primary_antibody1": "Goat Anti-tdT",
                    "immuno_secondary_antibody1": "Donkey anti-Goat IgG",
                    "gelation_mbs_start": "2023-11-09",
                    "date_of_storage_in_pbs_az_0_05_4c": "2023-12-14",
                }
            ],
            "imaging_queue_info": [
                {
                    "sample": "671477",
                    "imaging_start_date": "2024-01-08",
                    "microscope": "ExaSPIM",
                }
            ],
            "qc_sheet_info": [],
        }
        cls.exaspim_info = ExaSPIMInfo.model_validate(cls.exaspim_data)
        cls.mapper = ExaspimProceduresMapper(exaspim_info=cls.exaspim_info)

    def test_map_to_exaspim_procedures_structure(self):
        """Test complete procedures mapping returns correct structure"""
        subject_procs, specimen_procs = self.mapper.map_to_exaspim_procedures(
            "671477"
        )

        self.assertIsInstance(subject_procs, list)
        self.assertIsInstance(specimen_procs, list)
        self.assertGreater(len(subject_procs), 0)
        self.assertGreater(len(specimen_procs), 0)

    def test_subject_procedures_include_injection(self):
        """Test subject procedures include injection surgery"""
        subject_procs, _ = self.mapper.map_to_exaspim_procedures("671477")

        self.assertEqual(len(subject_procs), 1)
        surgery = subject_procs[0]
        self.assertIsInstance(surgery, Surgery)
        self.assertEqual(len(surgery.procedures), 2)
        self.assertTrue(
            all(isinstance(p, Injection) for p in surgery.procedures)
        )

    def test_specimen_procedures_count(self):
        """Test correct number of specimen procedures"""
        _, specimen_procs = self.mapper.map_to_exaspim_procedures("671477")

        self.assertEqual(len(specimen_procs), 5)

    def test_specimen_procedures_types(self):
        """Test specimen procedures have correct types"""
        _, specimen_procs = self.mapper.map_to_exaspim_procedures("671477")

        procedure_types = [p.procedure_type for p in specimen_procs]
        self.assertIn(SpecimenProcedureType.DELIPIDATION, procedure_types)
        self.assertIn(SpecimenProcedureType.IMMUNOLABELING, procedure_types)
        self.assertIn(SpecimenProcedureType.GELATION, procedure_types)
        self.assertIn(SpecimenProcedureType.EXPANSION, procedure_types)
        self.assertIn(SpecimenProcedureType.MOUNTING, procedure_types)

    def test_specimen_procedures_sorted_by_date(self):
        """Test specimen procedures are sorted chronologically"""
        _, specimen_procs = self.mapper.map_to_exaspim_procedures("671477")

        dates = [p.start_date for p in specimen_procs]
        self.assertEqual(dates, sorted(dates))

    def test_map_to_aind_procedures(self):
        """Test mapping to complete Procedures object"""
        subject_procs, specimen_procs = self.mapper.map_to_exaspim_procedures(
            "671477"
        )
        procedures = self.mapper.map_to_aind_procedures(
            "671477", specimen_procs, subject_procs
        )

        self.assertIsInstance(procedures, Procedures)
        self.assertEqual(procedures.subject_id, "671477")
        self.assertEqual(len(procedures.subject_procedures), 1)
        self.assertEqual(len(procedures.specimen_procedures), 5)

    def test_experimenters_propagated(self):
        """Test experimenters are propagated to all procedures"""
        _, specimen_procs = self.mapper.map_to_exaspim_procedures("671477")

        for proc in specimen_procs:
            self.assertIn("Rajvi Javeri", proc.experimenters)


class TestExaspimEdgeCases(TestCase):
    """Tests edge cases and error handling"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.mapper = ExaspimProceduresMapper()

    def test_empty_exaspim_info(self):
        """Test mapper handles empty ExaSPIMInfo"""
        empty_mapper = ExaspimProceduresMapper()
        subject_procs, specimen_procs = empty_mapper.map_to_exaspim_procedures(
            "test_id"
        )

        self.assertEqual(len(subject_procs), 0)
        self.assertEqual(len(specimen_procs), 0)

    def test_none_exaspim_info(self):
        """Test mapper handles None ExaSPIMInfo"""
        none_mapper = ExaspimProceduresMapper(exaspim_info=None)
        self.assertEqual(len(none_mapper.mouse_tracker_info), 0)
        self.assertEqual(len(none_mapper.sample_tracking_info), 0)

    def test_partial_data(self):
        """Test mapper handles partial data gracefully"""
        partial_data = {
            "mouse_tracker_info": [],
            "sample_tracking_info": [{"sample": "test"}],
            "imaging_queue_info": [],
            "qc_sheet_info": [],
        }
        partial_info = ExaSPIMInfo.model_validate(partial_data)
        mapper = ExaspimProceduresMapper(exaspim_info=partial_info)

        subject_procs, _ = mapper.map_to_exaspim_procedures("test")

        self.assertEqual(len(subject_procs), 0)

    def test_qc_notes_extraction_empty(self):
        """Test QC notes extraction with empty qc_sheet_info"""
        mapper = ExaspimProceduresMapper()
        notes = mapper._extract_qc_notes("perfusion")
        self.assertIsNone(notes)

    def test_qc_notes_extraction_invalid_category(self):
        """Test QC notes extraction with invalid category"""
        mapper = ExaspimProceduresMapper()
        notes = mapper._extract_qc_notes("invalid_category")
        self.assertIsNone(notes)

    def test_parse_experimenters_with_extra_whitespace(self):
        """Test parsing experimenters with extra whitespace in names"""
        sample_tracking = SampleTracking.model_construct(
            processing_lead="  Alice  ,  Bob  "
        )
        result = self.mapper._parse_experimenters(sample_tracking)
        self.assertEqual(result, ["Alice", "Bob"])

    def test_immunolabeling_with_empty_or_whitespace_catalog(self):
        """Test immunolabeling when catalog/lot are empty or whitespace"""
        sample_tracking = SampleTracking.model_construct(
            immuno_primary_ab_start_date="2023-01-01",
            immuno_primary_antibody1="Rabbit anti-GFP",
            primary_antibody1_catalog_num="   ",
            primary_antibody1_lot_num="",
        )
        result = self.mapper.build_immunolabeling(sample_tracking, "123", [])
        self.assertIsNotNone(result)
        self.assertEqual(len(result.procedure_details), 1)
        self.assertIsNone(result.procedure_details[0].rrid)
        self.assertIsNone(result.procedure_details[0].lot_number)

    def test_immunolabeling_secondary_with_empty_primary(self):
        """Test secondary antibody mapping when primary is empty"""
        sample_tracking = SampleTracking.model_construct(
            immuno_primary_ab_start_date="2023-01-01",
            immuno_secondary_antibody1="Donkey anti-Rabbit IgG",
            immuno_primary_antibody1="",
        )
        result = self.mapper.build_immunolabeling(sample_tracking, "123", [])
        self.assertIsNotNone(result)
        self.assertEqual(len(result.procedure_details), 1)

    def test_mounting_with_empty_or_whitespace_fields(self):
        """Test mounting when optional fields are empty or whitespace"""
        imaging_queue = ImagingQueue.model_construct(
            imaging_start_date="2024-01-08",
            microscope="   ",
            imaging_buffer="",
            signal_channel_s="",
            notes="   ",
        )
        result = self.mapper.build_mounting_and_imaging(
            imaging_queue, "123", []
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.procedure_details, [])
        self.assertIsNone(result.notes)

    def test_immunolabeling_notes_combinations(self):
        """Test immunolabeling notes with RRID and QC notes"""
        qc_sheet = QcSheet.model_construct(
            immuno_gross_anatomy_notes="Sample looks good"
        )
        mapper = ExaspimProceduresMapper(
            exaspim_info=ExaSPIMInfo.model_construct(
                mouse_tracker_info=[],
                sample_tracking_info=[],
                imaging_queue_info=[],
                qc_sheet_info=[qc_sheet],
            )
        )

        sample_with_rrid_and_qc = SampleTracking.model_construct(
            immuno_primary_ab_start_date="2023-01-01",
            immuno_primary_antibody1="Rabbit anti-GFP",
            primary_antibody_rrid="AB_123456",
            secondary_antibody_rrid="AB_789012",
        )
        result = mapper.build_immunolabeling(
            sample_with_rrid_and_qc, "123", []
        )
        self.assertIn("Primary RRID: AB_123456", result.notes)
        self.assertIn("Secondary RRID: AB_789012", result.notes)
        self.assertIn("Sample looks good", result.notes)

        mapper_no_qc = ExaspimProceduresMapper()
        sample_rrid_only = SampleTracking.model_construct(
            immuno_primary_ab_start_date="2023-01-01",
            immuno_primary_antibody1="Rabbit anti-GFP",
            primary_antibody_rrid="AB_123456",
        )
        result2 = mapper_no_qc.build_immunolabeling(
            sample_rrid_only, "123", []
        )
        self.assertIn("Primary RRID: AB_123456", result2.notes)
        self.assertNotIn("Secondary", result2.notes)

    def test_qc_notes_extraction(self):
        """Test QC notes extraction with multiple entries and empty values"""
        qc1 = QcSheet.model_construct(special_notes="Note 1")
        qc2 = QcSheet.model_construct(special_notes=None)
        qc3 = QcSheet.model_construct(special_notes="Note 2")
        mapper = ExaspimProceduresMapper(
            exaspim_info=ExaSPIMInfo.model_construct(
                mouse_tracker_info=[],
                sample_tracking_info=[],
                imaging_queue_info=[],
                qc_sheet_info=[qc1, qc2, qc3],
            )
        )
        notes = mapper._extract_qc_notes("special")
        self.assertEqual(notes, "Note 1; Note 2")

        perfusion_qc1 = QcSheet.model_construct(
            perfusion_dissection_quality_notes="Note 1"
        )
        perfusion_qc2 = QcSheet.model_construct(
            perfusion_dissection_quality_notes="Note 2"
        )
        mapper2 = ExaspimProceduresMapper(
            exaspim_info=ExaSPIMInfo.model_construct(
                mouse_tracker_info=[],
                sample_tracking_info=[],
                imaging_queue_info=[],
                qc_sheet_info=[perfusion_qc1, perfusion_qc2],
            )
        )
        perfusion_notes = mapper2._extract_qc_notes("perfusion")
        self.assertEqual(perfusion_notes, "Note 1; Note 2")

    def test_expansion_with_none_imaging_date(self):
        """Test expansion returns None when imaging_date is explicitly None"""
        sample_tracking = SampleTracking.model_construct(status="Imaged")
        result = self.mapper.build_expansion(sample_tracking, "123", None, [])
        self.assertIsNone(result)

    def test_immunolabeling_mass_parsing(self):
        """Test immunolabeling mass parsing with numeric strings and zero"""
        sample_with_string = SampleTracking.model_construct(
            immuno_primary_ab_start_date="2023-01-01",
            immuno_primary_antibody1="Rabbit anti-GFP",
            mass_of_primary_antibody1_used_per_brain_ug="10.5",
        )
        result = self.mapper.build_immunolabeling(
            sample_with_string, "123", []
        )
        self.assertEqual(result.procedure_details[0].target.mass, 10.5)

        sample_with_zero = SampleTracking.model_construct(
            immuno_primary_ab_start_date="2023-01-01",
            immuno_primary_antibody1="Rabbit anti-GFP",
            mass_of_primary_antibody1_used_per_brain_ug=0,
        )
        result2 = self.mapper.build_immunolabeling(sample_with_zero, "123", [])
        self.assertEqual(result2.procedure_details[0].target.mass, 0.0)

    def test_parse_date_edge_cases(self):
        """Test date parsing with unparseable and empty inputs"""
        self.assertIsNone(self.mapper._parse_date("not a date"))
        self.assertIsNone(self.mapper._parse_date("13/32/2023"))
        self.assertIsNone(self.mapper._parse_date("XYZ-ABC-DEF"))
        self.assertIsNone(self.mapper._parse_date("99/99/99"))

    def test_map_primary_antibody_target_edge_cases(self):
        """Test primary antibody target with empty and unknown names"""
        self.assertEqual(self.mapper._map_primary_antibody_target(""), "")
        self.assertEqual(self.mapper._map_primary_antibody_target("   "), "")
        self.assertEqual(
            self.mapper._map_primary_antibody_target("UNKNOWN_PROTEIN"),
            "UNKNOWN_PROTEIN",
        )

    def test_map_secondary_antibody_no_pattern_match(self):
        """Test secondary antibody when no pattern matches"""
        result = self.mapper._map_secondary_antibody_target(
            "Alexa Fluor 488 Conjugate",
            "Unknown Primary",
        )
        self.assertEqual(result, "Alexa Fluor 488 Conjugate")


if __name__ == "__main__":
    unittest_main()
