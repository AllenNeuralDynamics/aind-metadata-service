"""Module for mapping viral material data from slims"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from aind_metadata_service.slims.viral_injection.handler import (
    SlimsViralMaterialData,
    SlimsViralInjectionData,
)


class ViralMaterialData(BaseModel):
    """Model for viral material data."""

    content_category: Optional[str] = "Viral Materials"
    content_type: Optional[str] = None
    content_created_on: Optional[datetime] = None
    content_modified_on: Optional[datetime] = None
    viral_solution_type: Optional[str] = None
    virus_name: Optional[str] = None
    lot_number: Optional[str] = None
    lab_team: Optional[str] = None
    virus_type: Optional[str] = None
    virus_serotype: Optional[str] = None
    virus_plasmid_number: Optional[str] = None
    name: Optional[str] = None
    dose: Optional[Decimal] = None
    dose_unit: Optional[str] = None
    titer: Optional[Decimal] = None
    titer_unit: Optional[str] = "GC/ml"
    volume: Optional[Decimal] = None
    volume_unit: Optional[str] = None
    date_made: Optional[datetime] = None
    intake_date: Optional[datetime] = None
    storage_temperature: Optional[str] = None
    special_storage_guidelines: Optional[List[str]] = []
    special_handling_guidelines: Optional[List[str]] = []
    parent_barcode: Optional[str] = None
    parent_name: Optional[str] = None
    derivation_count: Optional[int] = 0
    ingredient_count: Optional[int] = 0


class ViralInjectionData(BaseModel):
    """ "Model for viral injection data."""

    content_category: Optional[str] = "Viral Materials"
    content_type: Optional[str] = "Viral Injection"
    content_created_on: Optional[datetime] = None
    content_modified_on: Optional[datetime] = None
    name: Optional[str] = None
    viral_injection_buffer: Optional[str] = None
    volume: Optional[Decimal] = None
    volume_unit: Optional[str] = None
    labeling_protein: Optional[str] = None
    date_made: Optional[datetime] = None
    intake_date: Optional[datetime] = None
    storage_temperature: Optional[str] = None
    special_storage_guidelines: Optional[List[str]] = []
    special_handling_guidelines: Optional[List[str]] = []
    derivation_count: Optional[int] = 0
    ingredient_count: Optional[int] = 0

    # From ORDER table
    assigned_mice: Optional[List[str]] = []
    requested_for_date: Optional[datetime] = None
    planned_injection_date: Optional[datetime] = None
    planned_injection_time: Optional[datetime] = None
    order_created_on: Optional[datetime] = None

    viral_materials: Optional[List[SlimsViralMaterialData]] = []


class SlimsViralInjectionlMapper:
    """Mapper class for Slims viral injections and materials"""

    def __init__(self, slims_vm_data: List[SlimsViralInjectionData]):
        """Class constructor"""
        self.slims_vm_data = slims_vm_data

    def map_info_from_slims(self) -> List[ViralInjectionData]:
        """Maps info from slims into data model"""

        vm_data = [
            ViralInjectionData.model_validate(m.model_dump())
            for m in self.slims_vm_data
        ]
        vm_data.sort(
            key=lambda m: (
                m.content_created_on is None,
                m.content_created_on,
            ),
            reverse=True,
        )
        return vm_data
