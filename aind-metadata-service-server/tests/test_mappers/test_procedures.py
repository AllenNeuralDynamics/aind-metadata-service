"""Module to test ProceduresMapper class"""

import json
import unittest
from datetime import date, datetime
from pathlib import Path

from aind_data_schema.core.procedures import (
    Perfusion,
    Procedures,
    RetroOrbitalInjection,
    Surgery,
)
from aind_labtracks_service_async_client.models.task import (
    Task as LabTracksTask,
)
from aind_sharepoint_service_async_client.models.las2020_list import (
    Las2020List,
)
from aind_sharepoint_service_async_client.models.nsb2019_list import (
    NSB2019List,
)
from aind_sharepoint_service_async_client.models.nsb2023_list import (
    NSB2023List,
)

from aind_metadata_service_server.mappers.procedures import (
    ProceduresMapper,
)

TEST_DIR = Path(__file__).parent / ".."
EXAMPLE_NSB2019_JSON = (
    TEST_DIR / "resources" / "nsb2019" / "raw" / "list_item1.json"
)
EXAMPLE_NSB2023_JSON = (
    TEST_DIR / "resources" / "nsb2023" / "raw" / "list_item1.json"
)
EXAMPLE_LAS2020_JSON = (
    TEST_DIR / "resources" / "las2020" / "raw" / "list_item1.json"
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
        with open(EXAMPLE_NSB2019_JSON) as f:
            nsb2019_contents = json.load(f)
        self.nsb_2019 = [NSB2019List.model_validate(nsb2019_contents)]
        with open(EXAMPLE_NSB2023_JSON) as f:
            nsb2023_contents = json.load(f)
        self.nsb_2023 = [NSB2023List.model_validate(nsb2023_contents)]
        with open(EXAMPLE_LAS2020_JSON) as f:
            las2020_contents = json.load(f)
        self.las2020 = [Las2020List.model_validate(las2020_contents)]

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
            nsb_2019=[],
            nsb_2023=[],
            nsb_present=[],
            las_2020=[],
        )
        expected_subject_procedures = [
            Surgery.model_construct(
                start_date=date(2022, 10, 11),
                experimenter_full_name="28803",
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
                experimenter_full_name="28803",
                iacuc_protocol="2002",
                animal_weight_prior=None,
                animal_weight_post=None,
                anaesthesia=None,
                notes=None,
                # Missing injection_volume and injection_eye
                procedures=[
                    RetroOrbitalInjection.model_construct(
                        injection_volume=None, injection_eye=None
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
            nsb_2019=self.nsb_2019,
            nsb_2023=self.nsb_2023,
            nsb_present=self.nsb_2023,
            las_2020=self.las2020,
        )
        procedures = mapper.map_responses_to_aind_procedures("115977")

        self.assertIsInstance(procedures, Procedures)
        self.assertEqual(procedures.subject_id, "115977")
        self.assertEqual(len(procedures.subject_procedures), 8)

    def test_map_responses_no_data(self):
        """Test mapping when no data sources have content"""
        mapper = ProceduresMapper(
            labtracks_tasks=[],
            nsb_2019=[],
            nsb_2023=[],
            nsb_present=[],
            las_2020=[],
        )

        procedures = mapper.map_responses_to_aind_procedures("0")
        self.assertIsNone(procedures)


if __name__ == "__main__":
    unittest.main()
