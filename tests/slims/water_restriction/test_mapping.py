"""Tests methods in mapping module"""

import os
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from aind_data_schema.core.procedures import WaterRestriction
from aind_data_schema_models.units import MassUnit, UnitlessUnit, VolumeUnit

from aind_metadata_service.slims.water_restriction.handler import (
    SlimsWaterRestrictionData,
)
from aind_metadata_service.slims.water_restriction.mapping import (
    SlimsWaterRestrictionMapper,
    WaterRestrictionData,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "water_restriction"
)


class TestSlimsWaterRestrictionMapper(unittest.TestCase):
    """Tests methods in SlimsWaterRestriction class"""

    def test_map_info_from_slims(self):
        """Tests map_info_from_slims method."""
        slims_wr_data = [
            SlimsWaterRestrictionData(
                content_event_created_on=1734119014103,
                subject_id="762287",
                start_date=1734119012354,
                end_date=None,
                assigned_by="person.name",
                target_weight_fraction=0.85,
                baseline_weight=28.23,
                weight_unit="g",
            )
        ]
        mapper = SlimsWaterRestrictionMapper(slims_wr_data=slims_wr_data)
        output = mapper.map_info_from_slims()
        expected_output = [
            WaterRestrictionData(
                content_event_created_on=datetime(
                    2024, 12, 13, 19, 43, 34, 103000, tzinfo=timezone.utc
                ),
                subject_id="762287",
                start_date=datetime(
                    2024, 12, 13, 19, 43, 32, 354000, tzinfo=timezone.utc
                ),
                end_date=None,
                assigned_by="person.name",
                target_weight_fraction=Decimal("0.85"),
                baseline_weight=Decimal("28.23"),
                weight_unit="g",
            )
        ]
        self.assertEqual(expected_output, output)

    def test_map_slims_info_to_water_restrictions(self):
        """Tests map_slims_info_to_water_restrictions method."""
        slims_wr_data = [
            SlimsWaterRestrictionData(
                content_event_created_on=1734119014103,
                subject_id="762287",
                start_date=1734119012354,
                end_date=None,
                assigned_by="person.name",
                target_weight_fraction=0.85,
                baseline_weight=28.23,
                weight_unit="g",
            )
        ]
        mapper = SlimsWaterRestrictionMapper(slims_wr_data=slims_wr_data)
        output = mapper.map_slims_info_to_water_restrictions()
        expected_output = [
            WaterRestriction.model_construct(
                procedure_type="Water restriction",
                target_fraction_weight=85,
                target_fraction_weight_unit=UnitlessUnit.PERCENT,
                minimum_water_per_day_unit=VolumeUnit.ML,
                baseline_weight=Decimal("28.23"),
                weight_unit=MassUnit.G,
                start_date=date(2024, 12, 13),
                end_date=None,
                minimum_water_per_day=1.0,
            )
        ]
        self.assertEqual(expected_output, output)

    def test_parse_mass_unit(self):
        """Test mass unit parsed as expected."""
        slims_wr_data = [SlimsWaterRestrictionData.model_construct()]
        mapper = SlimsWaterRestrictionMapper(slims_wr_data=slims_wr_data)
        with patch(
            "aind_metadata_service.slims.water_restriction.mapping"
            ".logging.warning"
        ) as mock_warn:
            result = mapper._parse_mass_unit("lbs")
            assert result == "lbs"
            mock_warn.assert_called_once_with(
                "Mass unit lbs not recognized. Returning it as is."
            )
        self.assertEqual(mapper._parse_mass_unit(None), MassUnit.G.value)
        self.assertEqual(mapper._parse_mass_unit("g"), MassUnit.G.value)


if __name__ == "__main__":
    unittest.main()
