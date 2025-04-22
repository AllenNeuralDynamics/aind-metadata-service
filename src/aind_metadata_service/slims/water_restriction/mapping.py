"""Module for mapping water restriction data from slims"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union

from aind_data_schema.core.procedures import WaterRestriction
from aind_data_schema_models.units import MassUnit
from pydantic import BaseModel

from aind_metadata_service.slims.water_restriction.handler import (
    SlimsWaterRestrictionData,
)


class WaterRestrictionData(BaseModel):
    """Model for water restriction data."""

    content_event_created_on: Optional[datetime] = None
    subject_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assigned_by: Optional[str] = None
    target_weight_fraction: Optional[Decimal] = None
    baseline_weight: Optional[Decimal] = None
    weight_unit: Optional[str] = None


class SlimsWaterRestrictionMapper:
    """Mapper class for Slims histology procedures"""

    def __init__(self, slims_wr_data: List[SlimsWaterRestrictionData]):
        """Class constructor"""
        self.slims_wr_data = slims_wr_data

    def map_info_from_slims(self) -> List[WaterRestrictionData]:
        """Maps info from slims into data model"""

        wr_data = [
            WaterRestrictionData.model_validate(m.model_dump())
            for m in self.slims_wr_data
        ]
        wr_data.sort(
            key=lambda m: (
                m.content_event_created_on is None,
                m.content_event_created_on,
            ),
            reverse=True,
        )
        return wr_data

    def map_slims_info_to_water_restrictions(self) -> List[WaterRestriction]:
        """Maps response from slims into WaterRestriction models"""
        wr_data = [
            WaterRestrictionData.model_validate(m.model_dump())
            for m in self.slims_wr_data
        ]
        water_restrictions = []
        for data in wr_data:
            wr = WaterRestriction.model_construct(
                start_date=data.start_date.date() if data.start_date else None,
                end_date=data.end_date.date() if data.end_date else None,
                assigned_by=data.assigned_by,
                target_fraction_weight=(
                    int(data.target_weight_fraction * 100)
                    if data.target_weight_fraction
                    else None
                ),
                baseline_weight=data.baseline_weight,
                weight_unit=self._parse_mass_unit(data.weight_unit),
                minimum_water_per_day=Decimal("1.0"),  # default value
            )
            water_restrictions.append(wr)
        return water_restrictions

    @staticmethod
    def _parse_mass_unit(
        value: Optional[str],
    ) -> Optional[Union[MassUnit, str]]:
        """Parse mass unit from string to MassUnit enum."""
        mass_unit_abbreviations = {
            "kg": MassUnit.KG,
            "g": MassUnit.G,
            "mg": MassUnit.MG,
            "ug": MassUnit.UG,
            "µg": MassUnit.UG,
            "ng": MassUnit.NG,
        }
        if not value:
            return MassUnit.G
        else:
            try:
                return mass_unit_abbreviations[value.lower()]
            except KeyError:
                logging.warning(
                    f"Mass unit {value} not recognized. Returning it as is."
                )
                return value
