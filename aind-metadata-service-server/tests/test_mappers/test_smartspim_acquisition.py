"""Tests methods in smartspim_acquisition module"""

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from aind_data_schema_models.devices import ImmersionMedium
from aind_dataverse_service_async_client.models import SmartSpimImagingModel

from aind_metadata_service_server.mappers.smartspim_acquisition import (
    SAMPLE_CHAMBER_NAME,
    TIME_NOTE,
    SmartSpimAcquisitionMapper,
)

RESOURCES_DIR = (
    Path(__file__).parent / ".." / "resources" / "dataverse"
).resolve()


class TestSmartSpimAcquisitionMapper(unittest.TestCase):
    """Tests SmartSpimAcquisitionMapper"""

    @classmethod
    def setUpClass(cls):
        """Load the example imaging response."""
        with open(RESOURCES_DIR / "smartspim_imaging_response.json") as f:
            cls.imaging = [
                SmartSpimImagingModel.model_validate(r) for r in json.load(f)
            ]

    def test_map_to_acquisitions(self):
        """Tests an imaging session is mapped to an acquisition."""
        acquisitions = SmartSpimAcquisitionMapper(
            imaging=self.imaging
        ).map_to_acquisitions()
        self.assertEqual(1, len(acquisitions))
        acquisition = acquisitions[0]
        performed = datetime(2026, 10, 13, tzinfo=timezone.utc)
        self.assertEqual("886598", acquisition.subject_id)
        self.assertEqual("886598", acquisition.specimen_id)
        self.assertEqual(performed, acquisition.acquisition_start_time)
        self.assertEqual(performed, acquisition.acquisition_end_time)
        self.assertEqual(["Person 1"], acquisition.experimenters)
        self.assertEqual("Heffer", acquisition.instrument_id)
        self.assertEqual("SmartSPIM", acquisition.acquisition_type)
        self.assertIsNone(acquisition.protocol_id)
        self.assertEqual(TIME_NOTE, acquisition.notes)
        self.assertEqual("SPIM_RPI", acquisition.coordinate_system.name)

        data_stream = acquisition.data_streams[0]
        self.assertEqual(performed, data_stream.stream_start_time)
        self.assertEqual(performed, data_stream.stream_end_time)
        self.assertEqual(
            ["Heffer", SAMPLE_CHAMBER_NAME], data_stream.active_devices
        )
        imaging_config, chamber_config = data_stream.configurations
        self.assertEqual("Heffer", imaging_config.device_name)
        self.assertEqual(
            ["488", "639"], [c.channel_name for c in imaging_config.channels]
        )
        self.assertEqual(
            [488, 639],
            [c.light_sources[0].wavelength for c in imaging_config.channels],
        )
        self.assertEqual(
            ImmersionMedium.OIL, chamber_config.chamber_immersion.medium
        )
        self.assertEqual(
            1.52, chamber_config.chamber_immersion.refractive_index
        )
        self.assertEqual(
            ImmersionMedium.EASYINDEX, chamber_config.sample_immersion.medium
        )

    def test_map_acquisition_minimal(self):
        """Tests a session with almost no data still maps."""
        data = SmartSpimImagingModel(
            subject_id="886598",
            instrument_id="SmartSPIM1",
            instrument_nickname="Heffer",
            protocol_id="dx.doi.org/10.17504/protocols.io.example",
        )
        acquisition = SmartSpimAcquisitionMapper(
            imaging=[data]
        ).map_to_acquisitions()[0]
        self.assertEqual("SmartSPIM1", acquisition.instrument_id)
        self.assertEqual(
            ["dx.doi.org/10.17504/protocols.io.example"],
            acquisition.protocol_id,
        )
        self.assertEqual([], acquisition.experimenters)
        self.assertIsNone(acquisition.coordinate_system)
        imaging_config, chamber_config = acquisition.data_streams[
            0
        ].configurations
        self.assertEqual([], imaging_config.channels)
        self.assertIsNone(chamber_config.chamber_immersion)
        self.assertIsNone(chamber_config.sample_immersion)

    def test_map_immersion(self):
        """Tests immersion medium labels and missing values."""
        expected = {
            "Cargille oil": ImmersionMedium.OIL,
            "diH2O": ImmersionMedium.WATER,
            "EasyIndex": ImmersionMedium.EASYINDEX,
            "Ethyl cinnamate": ImmersionMedium.ECI,
            "Optiplex and DMSO": ImmersionMedium.OTHER,
        }
        for label, medium in expected.items():
            with self.subTest(label=label):
                immersion = SmartSpimAcquisitionMapper._map_immersion(
                    label, "1.5"
                )
                self.assertEqual(medium, immersion.medium)
                self.assertEqual(1.5, immersion.refractive_index)
        self.assertIsNone(
            SmartSpimAcquisitionMapper._map_immersion(None, None)
        )
        partial = SmartSpimAcquisitionMapper._map_immersion("diH2O", None)
        self.assertEqual(ImmersionMedium.WATER, partial.medium)
        self.assertIsNone(partial.refractive_index)
        no_medium = SmartSpimAcquisitionMapper._map_immersion(None, "1.33")
        self.assertIsNone(no_medium.medium)

    def test_map_coordinate_system_missing_direction(self):
        """Tests no coordinate system is mapped if a direction is missing."""
        data = SmartSpimImagingModel(
            x_direction="Left_to_right", y_direction="Anterior_to_posterior"
        )
        self.assertIsNone(
            SmartSpimAcquisitionMapper._map_coordinate_system(data)
        )

    def test_map_channel_non_numeric(self):
        """Tests a channel without a wavelength has no light source."""
        channel = SmartSpimAcquisitionMapper._map_channel("Brightfield")
        self.assertEqual("Brightfield", channel.channel_name)
        self.assertEqual([], channel.light_sources)


if __name__ == "__main__":
    unittest.main()
