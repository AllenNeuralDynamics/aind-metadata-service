"""Tests methods in mapping module"""

import os
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from aind_metadata_service.slims.viral_injection.handler import (
    SlimsViralInjectionData,
    SlimsViralMaterialData,
)
from aind_metadata_service.slims.viral_injection.mapping import (
    SlimsViralInjectionMapper,
    ViralInjectionData,
    ViralMaterialData,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "viral_injection"
)


class TestSlimsViralInjectionMapper(unittest.TestCase):
    """Tests methods in SlimsSpimMapper class"""

    def test_map_info_from_slims(self):
        """Tests map_info_from_slims method."""
        slims_inj_data = [
            SlimsViralInjectionData(
                content_category="Viral Materials",
                content_type="Viral injection",
                content_created_on=None,
                content_modified_on=None,
                name="INJ00000002",
                viral_injection_buffer="AAV Buffer",
                volume=Decimal(str(98.56)),
                volume_unit="&mu;l",
                labeling_protein="tdTomato",
                date_made=1746014400000,
                intake_date=None,
                storage_temperature="4 C",
                special_storage_guidelines=["Light sensitive storage"],
                special_handling_guidelines=["BSL - 1"],
                mix_count=None,
                derivation_count=None,
                ingredient_count=None,
                assigned_mice=["614178"],
                requested_for_date=None,
                planned_injection_date=1746705600000,
                planned_injection_time=None,
                order_created_on=1746717795853,
                viral_materials=[
                    SlimsViralMaterialData(
                        content_category="Viral Materials",
                        content_type="Viral solution",
                        content_created_on=1746049926016,
                        content_modified_on=None,
                        viral_solution_type="Injection Dilution",
                        virus_name="7x-TRE-tDTomato",
                        lot_number="VT5355g",
                        lab_team="Molecular Anatomy",
                        virus_type="AAV",
                        virus_serotype="PhP.eB",
                        virus_plasmid_number="AiP300001",
                        name="VRS00000029",
                        dose=Decimal(str(180000000000)),
                        dose_unit=None,
                        titer=Decimal(str(24200000000000)),
                        titer_unit="GC/ml",
                        volume=Decimal(str(8.55)),
                        volume_unit="&mu;l",
                        date_made=1746049926079,
                        intake_date=None,
                        storage_temperature="-80 C",
                        special_storage_guidelines=[
                            "Avoid freeze - thaw cycles"
                        ],
                        special_handling_guidelines=["BSL - 1"],
                        parent_name=None,
                        mix_count=1,
                        derivation_count=0,
                        ingredient_count=0,
                    )
                ],
            )
        ]
        mapper = SlimsViralInjectionMapper(slims_vm_data=slims_inj_data)
        output = mapper.map_info_from_slims()
        expected_output = [
            ViralInjectionData(
                content_category="Viral Materials",
                content_type="Viral injection",
                content_created_on=None,
                content_modified_on=None,
                name="INJ00000002",
                viral_injection_buffer="AAV Buffer",
                volume=Decimal("98.56"),
                volume_unit="μl",
                labeling_protein="tdTomato",
                date_made=datetime(2025, 4, 30, 12, 0, tzinfo=timezone.utc),
                intake_date=None,
                storage_temperature="4 C",
                special_storage_guidelines=["Light sensitive storage"],
                special_handling_guidelines=["BSL - 1"],
                derivation_count=None,
                ingredient_count=None,
                mix_count=None,
                assigned_mice=["614178"],
                requested_for_date=None,
                planned_injection_date=datetime(
                    2025, 5, 8, 12, 0, tzinfo=timezone.utc
                ),
                planned_injection_time=None,
                order_created_on=datetime(
                    2025, 5, 8, 15, 23, 15, 853000, tzinfo=timezone.utc
                ),
                viral_materials=[
                    ViralMaterialData(
                        content_category="Viral Materials",
                        content_type="Viral solution",
                        content_created_on=datetime(
                            2025, 4, 30, 21, 52, 6, 16000, tzinfo=timezone.utc
                        ),
                        content_modified_on=None,
                        viral_solution_type="Injection Dilution",
                        virus_name="7x-TRE-tDTomato",
                        lot_number="VT5355g",
                        lab_team="Molecular Anatomy",
                        virus_type="AAV",
                        virus_serotype="PhP.eB",
                        virus_plasmid_number="AiP300001",
                        name="VRS00000029",
                        dose=Decimal("180000000000"),
                        dose_unit=None,
                        titer=Decimal("24200000000000"),
                        titer_unit="GC/ml",
                        volume=Decimal("8.55"),
                        volume_unit="μl",
                        date_made=datetime(
                            2025, 4, 30, 21, 52, 6, 79000, tzinfo=timezone.utc
                        ),
                        intake_date=None,
                        storage_temperature="-80 C",
                        special_storage_guidelines=[
                            "Avoid freeze - thaw cycles"
                        ],
                        special_handling_guidelines=["BSL - 1"],
                        parent_name=None,
                        derivation_count=0,
                        ingredient_count=0,
                        mix_count=1,
                    )
                ],
            )
        ]
        self.assertEqual(expected_output, output)


if __name__ == "__main__":
    unittest.main()
