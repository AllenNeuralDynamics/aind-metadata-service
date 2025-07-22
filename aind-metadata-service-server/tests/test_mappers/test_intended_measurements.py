"""Module to test IntendedMeasurementMapper class"""

import unittest
import json
from pathlib import Path
from aind_metadata_service_server.mappers.intended_measurements import (
    IntendedMeasurementMapper,
)
from aind_sharepoint_service_async_client.models.nsb2023_list import (
    NSB2023List,
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


if __name__ == "__main__":
    unittest.main()
