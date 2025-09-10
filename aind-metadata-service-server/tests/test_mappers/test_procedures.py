"""Module to test ProceduresMapper class"""

import json
import unittest
from unittest.mock import patch
from datetime import date, datetime
from pathlib import Path

from aind_data_schema.components.injection_procedures import (
    Injection,
    InjectionDynamics,
)
from aind_data_schema.components.subject_procedures import (
    Perfusion,
    WaterRestriction,
)
from aind_data_schema.components.surgery_procedures import (
    BrainInjection,
    Craniotomy,
    ProtectiveMaterial,
)
from aind_data_schema.core.procedures import (
    Procedures,
    Surgery,
)
from aind_data_schema_models.mouse_anatomy import InjectionTargets
from aind_labtracks_service_async_client.models.task import (
    Task as LabTracksTask,
)
from aind_sharepoint_service_async_client.models.las2020_list import (
    Las2020List,
)
from aind_sharepoint_service_async_client.models.nsb2019_list import (
    NSB2019List,
)
from aind_slims_service_async_client.models import SlimsWaterRestrictionData
from aind_slims_service_async_client.models.slims_histology_data import (
    HistologyWashData,
    SlimsHistologyData,
)
from aind_smartsheet_service_async_client.models import PerfusionsModel

from aind_metadata_service_server.mappers.procedures import (
    ProceduresMapper,
    ProtocolNames,
)
from aind_metadata_service_server.models import (
    ProtocolInformation,
)
from aind_data_schema_models.units import MassUnit, UnitlessUnit, VolumeUnit

TEST_DIR = Path(__file__).parent / ".."
EXAMPLE_LAS2020_JSON = (
    TEST_DIR / "resources" / "las2020" / "raw" / "list_item1.json"
)
EXAMPLE_NSB2019_JSON = (
    TEST_DIR / "resources" / "nsb2019" / "raw" / "list_item1.json"
)


class TestProcedures(unittest.TestCase):
    """Test procedures mapper functionality"""

    def setUp(self):
        """Set up test data before each test method"""
        self.labtracks_tasks = [
            LabTracksTask(
                id="0",
                type_name="Perfusion Gel",
                date_start=datetime(2022, 10, 11, 0, 0),
                date_end=datetime(2022, 10, 11, 4, 30),
                investigator_id="28803",
                task_object="115977",
                protocol_number="2002",
                task_status="F",
            ),
            LabTracksTask(
                id="0",
                type_name="Perfusion Gel",
                date_start=datetime(2022, 10, 11, 0, 0),
                date_end=datetime(2022, 10, 11, 4, 30),
                investigator_id="28803",
                task_object="115977",
                protocol_number="2002",
                task_status="C",
            ),
            LabTracksTask(
                id="10000",
                type_name="RO Injection VGT",
                date_start=datetime(2022, 5, 11, 0, 0),
                date_end=datetime(2022, 5, 12, 0, 0),
                investigator_id="28803",
                task_object="115977",
                protocol_number="2002",
                task_status="F",
            ),
        ]
        self.slims_water_restriction = [
            SlimsWaterRestrictionData(
                content_event_created_on=1734119014103,
                subject_id="115977",
                start_date=datetime.fromtimestamp(1734119012.354),
                end_date=None,
                assigned_by="person.name",
                target_weight_fraction="0.85",
                baseline_weight="28.23",
                weight_unit="g",
            )
        ]
        self.slims_histology = [
            SlimsHistologyData(
                procedure_name="SmartSPIM Labeling",
                protocol_id=None,
                protocol_name=None,
                washes=[
                    HistologyWashData(
                        wash_name="Primary Antibody Wash",
                        wash_type=None,
                        start_time=datetime.fromtimestamp(1738688400),
                        end_time=datetime.fromtimestamp(1738781400),
                        modified_by="PersonM",
                        reagents=[],
                        mass="10.2",
                    ),
                    HistologyWashData(
                        wash_name="Secondary Antibody Wash",
                        wash_type=None,
                        start_time=datetime.fromtimestamp(1738688400),
                        end_time=datetime.fromtimestamp(1738781400),
                        modified_by="PersonM",
                        reagents=[],
                        mass=None,
                    ),
                ],
                subject_id="115977",
            ),
        ]
        self.perfusions_sheet = [
            PerfusionsModel(
                subject_id="115977.0",
                var_date=date(2023, 10, 2),
                experimenter="Person S",
                iacuc_protocol=(
                    "2109 - Analysis of brain - wide neural circuits in the"
                    " mouse"
                ),
                animal_weight_prior__g="22.0",
                output_specimen_id_s="115977.0",
                postfix_solution="1xPBS",
                notes="Good",
            )
        ]
        with open(EXAMPLE_LAS2020_JSON) as f:
            las2020_contents = json.load(f)
        self.las2020 = [Las2020List.model_validate(las2020_contents)]
        with open(EXAMPLE_NSB2019_JSON) as f:
            nsb2019_contents = json.load(f)
        self.nsb2019 = [NSB2019List.model_validate(nsb2019_contents)]

    def test_map_labtracks_unknown_task_to_none(self):
        """Test mapping LabTracksTask to None"""
        task = self.labtracks_tasks[0]
        task.type_name = "Unknown Task Type"
        surgery = ProceduresMapper._map_labtracks_task_to_aind_surgery(task)
        self.assertIsNone(surgery)

    def test_map_responses_only_labtracks(self):
        """Test mapping with only LabTracks tasks"""
        mapper = ProceduresMapper(
            labtracks_tasks=self.labtracks_tasks,
            las_2020=[],
        )
        expected_subject_procedures = [
            Surgery.model_construct(
                start_date=date(2022, 10, 11),
                experimenters=["28803"],
                iacuc_protocol="2002",
                animal_weight_prior=None,
                animal_weight_post=None,
                anaesthesia=None,
                notes=None,
                # Perfusion missing protocol_id
                procedures=[
                    Perfusion.model_construct(output_specimen_ids={"115977"})
                ],
            ),
            Surgery.model_construct(
                start_date=date(2022, 5, 11),
                experimenters=["28803"],
                iacuc_protocol="2002",
                animal_weight_prior=None,
                animal_weight_post=None,
                anaesthesia=None,
                notes=None,
                # Missing injection_volume and injection_eye
                procedures=[
                    Injection.model_construct(
                        targeted_structure=InjectionTargets.RETRO_ORBITAL,
                    )
                ],
            ),
        ]
        procedures = mapper.map_responses_to_aind_procedures("115977")
        self.assertIsInstance(procedures, Procedures)
        self.assertEqual(
            procedures.subject_procedures, expected_subject_procedures
        )

    def test_map_responses_to_aind_procedures(self):
        """Test mapping with NSB2019 and NSB2023 data"""
        mapper = ProceduresMapper(
            labtracks_tasks=self.labtracks_tasks,
            las_2020=self.las2020,
            nsb_2019=self.nsb2019,
            slims_water_restriction=self.slims_water_restriction,
            slims_histology=self.slims_histology,
            smartsheet_perfusion=self.perfusions_sheet,
        )
        procedures = mapper.map_responses_to_aind_procedures("115977")

        self.assertIsInstance(procedures, Procedures)
        self.assertEqual(procedures.subject_id, "115977")
        self.assertEqual(len(procedures.subject_procedures), 8)
        self.assertEqual(len(procedures.specimen_procedures), 0)

    def test_map_responses_no_data(self):
        """Test mapping when no data sources have content"""
        mapper = ProceduresMapper(
            labtracks_tasks=[],
            las_2020=[],
            nsb_2019=[],
        )

        procedures = mapper.map_responses_to_aind_procedures("0")
        self.assertIsNone(procedures)

    def test_integrate_protocols(self):
        """Tests that protocols are integrated into procedures as expected"""
        nano_protocol = ProtocolInformation(
            protocol_type="Surgical Procedures",
            procedure_name="Injection Nanoject",
            protocol_name="Injection Nanoject",
            doi="dx.doi.org/some/doi/1",
            version=1.0,
            protocol_collection=None,
        )
        surgery_protocol = ProtocolInformation.model_construct(
            protocol_type="Surgical Procedures",
            procedure_name="Surgery",
            protocol_name="Surgery",
            doi="dx.doi.org/some/doi/2",
            version=None,
            protocol_collection=None,
        )
        nano_name = "Injection of Viral Tracers by Nanoject V.4"
        surgery_name = "General Set-Up and Take-Down for Rodent Neurosurgery"
        protocols_mapping = {
            nano_name: nano_protocol,
            surgery_name: surgery_protocol,
        }
        dynamics = InjectionDynamics.model_construct(
            volume=50,
        )
        nanoject_inj = BrainInjection.model_construct(dynamics=[dynamics])
        surgery = Surgery.model_construct(
            experimenters=["NSB-123"], procedures=[nanoject_inj]
        )
        procedures = Procedures.model_construct(
            subject_id="12345",
            subject_procedures=[surgery],
        )
        merged = ProceduresMapper().integrate_protocols_into_aind_procedures(
            procedures, protocols_mapping
        )
        self.assertEqual(
            merged.subject_procedures[0].protocol_id, "dx.doi.org/some/doi/2"
        )
        self.assertEqual(
            merged.subject_procedures[0].procedures[0].protocol_id,
            "dx.doi.org/some/doi/1",
        )

    def test_integrate_protocols_no_procedures(self):
        """Tests protocol integration when Surgery has no procedures"""
        surgery_protocol = ProtocolInformation.model_construct(
            protocol_type="Surgical Procedures",
            procedure_name="Surgery",
            protocol_name="Surgery",
            doi="dx.doi.org/some/doi/2",
            version="1.0",
            protocol_collection=None,
        )
        surgery_name = "General Set-Up and Take-Down for Rodent Neurosurgery"
        protocols_mapping = {
            surgery_name: surgery_protocol,
        }
        surgery = Surgery.model_construct(experimenters=["NSB-123"])
        procedures = Procedures.model_construct(
            subject_id="12345", subject_procedures=[surgery]
        )
        merged = ProceduresMapper().integrate_protocols_into_aind_procedures(
            procedures, protocols_mapping
        )
        self.assertEqual(
            merged.subject_procedures[0].protocol_id, "dx.doi.org/some/doi/2"
        )

    def test_get_protocols_list(self):
        """Tests that protocols list is created as expected"""
        ionto_inj = BrainInjection.model_construct(
            dynamics=[InjectionDynamics.model_construct(injection_current=50)]
        )
        cran = Craniotomy.model_construct(
            protective_material=ProtectiveMaterial.DURAGEL
        )
        surgery = Surgery.model_construct(procedures=[ionto_inj, cran])
        procedures = Procedures.model_construct(
            subject_id="000000", subject_procedures=[surgery]
        )
        protocols_list = ProceduresMapper().get_protocols_list(procedures)
        expected_list = [
            ProtocolNames.SURGERY.value,
            ProtocolNames.INJECTION_IONTOPHORESIS.value,
            ProtocolNames.DURAGEL_APPLICATION.value,
        ]
        self.assertEqual(expected_list, protocols_list)

    def test_get_protocols_list_missing_procedures(self):
        """Tests protocols list when Surgery has no procedures attribute"""
        surgery = Surgery.model_construct()
        procedures = Procedures(
            subject_id="000000", subject_procedures=[surgery]
        )
        protocols_list = ProceduresMapper().get_protocols_list(procedures)
        expected_list = [
            ProtocolNames.SURGERY.value,
        ]
        self.assertEqual(expected_list, protocols_list)

    def test_map_slims_info_to_water_restrictions(self):
        """Tests map_slims_info_to_water_restrictions method."""
        slims_water_restriction = [
            SlimsWaterRestrictionData(
                content_event_created_on=1734119014103,
                subject_id="762287",
                start_date=datetime.fromtimestamp(1734119012.354),
                end_date=None,
                assigned_by="person.name",
                target_weight_fraction="0.85",
                baseline_weight="28.23",
                weight_unit="g",
            )
        ]
        mapper = ProceduresMapper(
            slims_water_restriction=slims_water_restriction
        )
        output = mapper._map_slims_response_to_aind_water_restrictions()
        expected_output = [
            WaterRestriction.model_construct(
                procedure_type="Water restriction",
                target_fraction_weight=85,
                target_fraction_weight_unit=UnitlessUnit.PERCENT,
                minimum_water_per_day_unit=VolumeUnit.ML,
                baseline_weight=28.23,
                weight_unit=MassUnit.G,
                start_date=date.fromtimestamp(1734119012.354),
                end_date=None,
                minimum_water_per_day=1.0,
            )
        ]
        self.assertEqual(output, expected_output)

    def test_parse_mass_unit(self):
        """Test mass unit parsed as expected."""
        slims_water_restriction = [SlimsWaterRestrictionData.model_construct()]
        mapper = ProceduresMapper(
            slims_water_restriction=slims_water_restriction
        )
        with patch(
            "aind_metadata_service_server.mappers.procedures.logging.warning"
        ) as mock_warn:
            result = mapper._parse_mass_unit("lbs")
            self.assertEqual(result, "lbs")
            mock_warn.assert_called_once_with(
                "Mass unit lbs not recognized. Returning it as is."
            )
        self.assertEqual(mapper._parse_mass_unit(None), MassUnit.G)
        self.assertEqual(mapper._parse_mass_unit("g"), MassUnit.G)


if __name__ == "__main__":
    unittest.main()
