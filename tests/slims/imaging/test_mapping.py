"""Tests methods in mapping module"""

import os
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from aind_metadata_service.slims.imaging.handler import SlimsSpimData
from aind_metadata_service.slims.imaging.mapping import (
    SlimsSpimMapper,
    SpimData,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "imaging"
)


class TestSlimsSpimMapper(unittest.TestCase):
    """Tests methods in SlimsSpimMapper class"""

    def test_map_info_from_slims(self):
        """Tests map_info_from_slims method."""
        slims_spim_data = [
            SlimsSpimData(
                experiment_run_created_on=1739383241200,
                specimen_id="BRN00000018",
                subject_id="744742",
                protocol_name="Imaging cleared mouse brains on SmartSPIM",
                protocol_id=(
                    "<a href="
                    '"https://dx.doi.org/10.17504/protocols.io.3byl4jo1rlo5/'
                    'v1" '
                    'target="_blank" '
                    'rel="nofollow noopener noreferrer">'
                    "Imaging cleared mouse brains on SmartSPIM"
                    "</a>"
                ),
                date_performed=1739383260000,
                chamber_immersion_medium="Ethyl Cinnamate",
                sample_immersion_medium="Ethyl Cinnamate",
                chamber_refractive_index=Decimal(str(1.557)),
                sample_refractive_index=Decimal(str(1.557)),
                instrument_id="440_SmartSPIM1_20240327",
                experimenter_name="Person R",
                z_direction="Superior to Inferior",
                y_direction="Anterior to Posterior",
                x_direction="Left to Right",
                imaging_channels=[
                    "Laser = 488; Emission Filter = 525/45",
                    "Laser = 561; Emission Filter = 593/40",
                    "Laser = 639; Emission Filter = 667/30",
                ],
                stitching_channels="Laser = 639, Emission Filter = 667/30",
                ccf_registration_channels=(
                    "Laser = 639, Emission Filter = 667/30"
                ),
                cell_segmentation_channels=None,
            )
        ]
        mapper = SlimsSpimMapper(slims_spim_data=slims_spim_data)
        output = mapper.map_info_from_slims()
        expected_output = [
            SpimData(
                experiment_run_created_on=datetime(
                    2025, 2, 12, 18, 0, 41, 200000, tzinfo=timezone.utc
                ),
                specimen_id="BRN00000018",
                subject_id="744742",
                protocol_name="Imaging cleared mouse brains on SmartSPIM",
                protocol_id=(
                    "https://dx.doi.org/10.17504/protocols.io.3byl4jo1rlo5/v1"
                ),
                date_performed=datetime(
                    2025, 2, 12, 18, 1, tzinfo=timezone.utc
                ),
                chamber_immersion_medium="Ethyl Cinnamate",
                sample_immersion_medium="Ethyl Cinnamate",
                chamber_refractive_index=Decimal("1.557"),
                sample_refractive_index=Decimal("1.557"),
                instrument_id="440_SmartSPIM1_20240327",
                experimenter_name="Person R",
                z_direction="Superior to Inferior",
                y_direction="Anterior to Posterior",
                x_direction="Left to Right",
                imaging_channels=[
                    "Laser = 488; Emission Filter = 525/45",
                    "Laser = 561; Emission Filter = 593/40",
                    "Laser = 639; Emission Filter = 667/30",
                ],
                stitching_channels="Laser = 639, Emission Filter = 667/30",
                ccf_registration_channels=(
                    "Laser = 639, Emission Filter = 667/30"
                ),
                cell_segmentation_channels=None,
            )
        ]

        self.assertEqual(expected_output, output)


if __name__ == "__main__":
    unittest.main()
