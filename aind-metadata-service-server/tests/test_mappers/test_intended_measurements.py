"""Module to test IntendedMeasurementMapper class"""

import json
import unittest
from pathlib import Path

from aind_sharepoint_service_async_client.models.nsb2023_list import (
    NSB2023List,
)

from aind_metadata_service_server.mappers.intended_measurements import (
    IntendedMeasurementMapper,
)
from aind_metadata_service_server.models import IntendedMeasurementInformation

TEST_DIR = Path(__file__).parent / ".."
EXAMPLE_NSB2023_INTENDED_MEASUREMENTS = (
    TEST_DIR / "resources" / "nsb2023" / "nsb2023_intended_measurements.json"
)


class TestIntendedMeasurementMapper(unittest.TestCase):
    """Class to test methods of IntendedMeasurementMapper"""

    def setUp(self):
        """Set up test data for test methods"""
        with open(EXAMPLE_NSB2023_INTENDED_MEASUREMENTS) as f:
            nsb2023_raw = json.load(f)
        self.nsb2023_intended = NSB2023List.model_validate(nsb2023_raw)
        self.expected_intended = [
            IntendedMeasurementInformation(
                fiber_name=None,
                intended_measurement_R="acetylcholine",
                intended_measurement_G="calcium",
                intended_measurement_B="GABA",
                intended_measurement_Iso="control",
            ),
            IntendedMeasurementInformation(
                fiber_name="Fiber_0",
                intended_measurement_R="acetylcholine",
                intended_measurement_G="dopamine",
                intended_measurement_B="GABA",
                intended_measurement_Iso="control",
            ),
            IntendedMeasurementInformation(
                fiber_name="Fiber_1",
                intended_measurement_R="acetylcholine",
                intended_measurement_G="dopamine",
                intended_measurement_B="glutamate",
                intended_measurement_Iso="control",
            ),
            IntendedMeasurementInformation(
                fiber_name="Fiber_0",
                intended_measurement_R="norepinephrine",
                intended_measurement_G="calcium",
                intended_measurement_B="glutamate",
                intended_measurement_Iso="voltage",
            ),
        ]

    def test_intended_measurement_data_mapped(self):
        """Test that intended measurements are mapped correctly."""
        mapper = IntendedMeasurementMapper(
            nsb_2023=[self.nsb2023_intended], nsb_present=[NSB2023List()]
        )
        intended_measurements = mapper.map_responses_to_intended_measurements(
            subject_id="000000"
        )
        self.assertEqual(intended_measurements, self.expected_intended)

    def test_no_data_returns_empty(self):
        """Test that an empty list is returned if there is no data."""
        mapper = IntendedMeasurementMapper(nsb_2023=[], nsb_present=[])
        measurements = mapper.map_responses_to_intended_measurements(
            subject_id="no_such_subject"
        )
        self.assertEqual(measurements, [])

    def test_measurements_with_none_coordinates_filtered_out(self):
        """Test measurements with None coordinates without fiber names."""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 1,
            "Burr_x0020_hole_x0020_1": "Stereotaxic Injection & Fiber Implant",
            "Burr1_x0020_Perform_x0020_During": "Initial Surgery",
            "Burr_x0020_Hole_x0020_1_x0020_st": "Complete",
            "Burr_x0020_1_x0020_intended_x0020": "acetylcholine",
            "Burr_x0020_1_x0020_intended_x0021": "dopamine",
            "Burr_x0020_1_x0020_intended_x0022": "GABA",
            "Burr_x0020_1_x0020_intended_x0023": "control",
        }
        nsb_model = NSB2023List.model_validate(nsb_data)
        mapper = IntendedMeasurementMapper(
            nsb_2023=[nsb_model], nsb_present=[]
        )
        measurements = mapper.map_responses_to_intended_measurements(
            subject_id="test_subject"
        )
        self.assertEqual(len(measurements), 1)
        self.assertIsNone(measurements[0].fiber_name)
        self.assertEqual(
            measurements[0].intended_measurement_R, "acetylcholine"
        )
        self.assertEqual(measurements[0].intended_measurement_G, "dopamine")

    def test_measurements_with_all_none_values(self):
        """Test that measurements with None values with fiber names."""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 2,
            "Burr_x0020_hole_x0020_1": "Stereotaxic Injection & Fiber Implant",
            "Burr1_x0020_Perform_x0020_During": "Initial Surgery",
            "Burr_x0020_Hole_x0020_1_x0020_st": "Complete",
            "Virus_x0020_A_x002f_P": 1.0,
            "Virus_x0020_M_x002f_L": 1.5,
            "Burr_x0020_1_x0020_intended_x0020": None,
            "Burr_x0020_1_x0020_intended_x0021": None,
            "Burr_x0020_1_x0020_intended_x0022": None,
            "Burr_x0020_1_x0020_intended_x0023": None,
        }
        nsb_model = NSB2023List.model_validate(nsb_data)
        mapper = IntendedMeasurementMapper(
            nsb_2023=[nsb_model], nsb_present=[]
        )
        measurements = mapper.map_responses_to_intended_measurements(
            subject_id="test_subject"
        )
        # Since coordinates exist, should return measurement with fiber name
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0].fiber_name, "Fiber_0")
        self.assertIsNone(measurements[0].intended_measurement_R)
        self.assertIsNone(measurements[0].intended_measurement_G)
        self.assertIsNone(measurements[0].intended_measurement_B)
        self.assertIsNone(measurements[0].intended_measurement_Iso)

    def test_measurements_with_partial_values_included(self):
        """Test that measurements with at least one value are included."""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 3,
            "Burr_x0020_hole_x0020_1": "Stereotaxic Injection & Fiber Implant",
            "Burr1_x0020_Perform_x0020_During": "Initial Surgery",
            "Burr_x0020_Hole_x0020_1_x0020_st": "Complete",
            "Virus_x0020_A_x002f_P": 1.0,
            "Virus_x0020_M_x002f_L": 1.5,
            "Burr_x0020_1_x0020_intended_x0020": "acetylcholine",
            "Burr_x0020_1_x0020_intended_x0021": None,
            "Burr_x0020_1_x0020_intended_x0022": None,
            "Burr_x0020_1_x0020_intended_x0023": None,
        }
        nsb_model = NSB2023List.model_validate(nsb_data)
        mapper = IntendedMeasurementMapper(
            nsb_2023=[nsb_model], nsb_present=[]
        )
        measurements = mapper.map_responses_to_intended_measurements(
            subject_id="test_subject"
        )
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0].fiber_name, "Fiber_0")
        self.assertEqual(
            measurements[0].intended_measurement_R, "acetylcholine"
        )
        self.assertIsNone(measurements[0].intended_measurement_G)

    def test_measurements_without_during_info(self):
        """Test measurements without during info"""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 4,
            "Burr_x0020_hole_x0020_1": "Stereotaxic Injection & Fiber Implant",
            "Burr_x0020_Hole_x0020_1_x0020_st": "Complete",
            "Virus_x0020_A_x002f_P": 1.0,
            "Virus_x0020_M_x002f_L": 1.5,
            "Burr_x0020_1_x0020_intended_x0020": None,
            "Burr_x0020_1_x0020_intended_x0021": None,
            "Burr_x0020_1_x0020_intended_x0022": None,
            "Burr_x0020_1_x0020_intended_x0023": None,
        }
        nsb_model = NSB2023List.model_validate(nsb_data)
        mapper = IntendedMeasurementMapper(
            nsb_2023=[nsb_model], nsb_present=[]
        )
        measurements = mapper.map_responses_to_intended_measurements(
            subject_id="test_subject"
        )
        # Even without during info, measurements with coordinates are included
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0].fiber_name, "Fiber_0")
        self.assertIsNone(measurements[0].intended_measurement_R)
        self.assertIsNone(measurements[0].intended_measurement_G)
        self.assertIsNone(measurements[0].intended_measurement_B)
        self.assertIsNone(measurements[0].intended_measurement_Iso)

    def test_measurements_with_none(self):
        """Test measurements with None values."""
        nsb_data = {
            "FileSystemObjectType": 0,
            "Id": 3,
            "Burr_x0020_hole_x0020_1": "Stereotaxic Injection & Fiber Implant",
            "Burr1_x0020_Perform_x0020_During": "Initial Surgery",
            "Burr_x0020_Hole_x0020_1_x0020_st": "Complete",
            "Virus_x0020_A_x002f_P": 1.0,
            "Virus_x0020_M_x002f_L": 1.5,
            "Burr_x0020_1_x0020_intended_x0020": "acetylcholine",
            "Burr_x0020_1_x0020_intended_x0021": "None",
            "Burr_x0020_1_x0020_intended_x0022": "Select...",
            "Burr_x0020_1_x0020_intended_x0023": "N/A",
        }
        nsb_model = NSB2023List.model_validate(nsb_data)
        mapper = IntendedMeasurementMapper(
            nsb_2023=[nsb_model], nsb_present=[]
        )
        measurements = mapper.map_responses_to_intended_measurements(
            subject_id="test_subject"
        )
        print(measurements)
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0].fiber_name, "Fiber_0")
        self.assertEqual(
            measurements[0].intended_measurement_R, "acetylcholine"
        )
        self.assertEqual(measurements[0].intended_measurement_G, "None")
        self.assertIsNone(measurements[0].intended_measurement_B)
        self.assertIsNone(measurements[0].intended_measurement_Iso)


if __name__ == "__main__":
    unittest.main()
