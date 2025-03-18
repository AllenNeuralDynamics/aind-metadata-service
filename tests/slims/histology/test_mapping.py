"""Tests methods in mapping module"""

import json
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path

from aind_data_schema_models.specimen_procedure_types import (
    SpecimenProcedureType,
)

from aind_metadata_service.slims.histology.handler import (
    SlimsHistologyData,
    SlimsReagentData,
    SlimsWashData,
)
from aind_metadata_service.slims.histology.mapping import (
    HistologyData,
    SlimsHistologyMapper,
    WashData,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "histology"
)


class TestHistData(unittest.TestCase):
    """Tests validators in SpimData model"""

    def test_parse_procedure_name(self):
        """Tests parse_procedure_name"""
        names = [
            "SmartSPIM Delipidation",
            "SmartSPIM Labeling",
            "SmartSPIM Refractive Index Matching",
            "ExaSPIM Delipidation",
            "ExaSPIM Labeling",
            "ExaSPIM Gelation",
            "ExaSPIM Expansion",
            "UNKNOWN",
            None,
        ]
        expected_types = [
            SpecimenProcedureType.DELIPIDATION,
            SpecimenProcedureType.IMMUNOLABELING,
            SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING,
            SpecimenProcedureType.DELIPIDATION,
            SpecimenProcedureType.IMMUNOLABELING,
            SpecimenProcedureType.GELATION,
            SpecimenProcedureType.EXPANSION,
            None,
            None,
        ]

        outputs = []
        for name in names:
            output = HistologyData(procedure_name=name).procedure_type
            outputs.append(output)
        self.assertEqual(expected_types, outputs)


class TestSlimsHistologyMapper(unittest.TestCase):
    """Tests methods in SlimsHistMapper class"""

    def setUp(self):
        """Set up test data"""
        with open(f"{RESOURCES_DIR}/slims_hist_data.json", "r") as f:
            slims_hist_data_json = json.load(f)
        self.slims_hist_data = [
            SlimsHistologyData.model_validate(data)
            for data in slims_hist_data_json
        ]
        with open(
            f"{RESOURCES_DIR}/expected_histology_procedures.json", "r"
        ) as f:
            self.expected_procedures_json = json.load(f)
        self.mapper = SlimsHistologyMapper(
            slims_hist_data=self.slims_hist_data
        )

    def test_map_info_from_slims(self):
        """Tests map_info_from_slims method."""
        slims_hist_data = slims_hist_data = [
            SlimsHistologyData(
                procedure_name="SmartSPIM Refractive Index Matching",
                experiment_run_created_on=1738175075574,
                specimen_id="BRN00000002",
                subject_id="754372",
                protocol_id=(
                    '<a href="https://www.protocols.io/edit/'
                    'refractive-index-matching-ethyl-cinnamate-cukpwuvn" '
                    'target="_blank" '
                    'rel="nofollow noopener noreferrer">'
                    "Refractive Index Matching - Ethyl Cinnamate</a>"
                ),
                protocol_name=(
                    "Refractive Index Matching - Ethyl Cinnamate (UNPUBLISHED)"
                ),
                washes=[
                    SlimsWashData(
                        wash_name="Refractive Index Matching Wash",
                        wash_type="Refractive Index Matching",
                        start_time=1737744000000,
                        end_time=1738003200000,
                        modified_by="PersonM",
                        reagents=[
                            SlimsReagentData(
                                name="112372-100G",
                                source=None,
                                lot_number="stbk5149",
                            )
                        ],
                    )
                ],
            )
        ]
        mapper = SlimsHistologyMapper(slims_hist_data=slims_hist_data)
        output = mapper.map_info_from_slims()
        expected_output = [
            HistologyData(
                procedure_name="SmartSPIM Refractive Index Matching",
                experiment_run_created_on=datetime(
                    2025, 1, 29, 18, 24, 35, 574000, tzinfo=timezone.utc
                ),
                specimen_id="BRN00000002",
                subject_id="754372",
                protocol_id=(
                    "https://www.protocols.io/edit/"
                    "refractive-index-matching-ethyl-cinnamate-cukpwuvn"
                ),
                protocol_name=(
                    "Refractive Index Matching - Ethyl Cinnamate (UNPUBLISHED)"
                ),
                procedure_type=SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING,
                washes=[
                    WashData(
                        wash_name="Refractive Index Matching Wash",
                        wash_type="Refractive Index Matching",
                        start_time=datetime(
                            2025, 1, 24, 18, 40, tzinfo=timezone.utc
                        ),
                        end_time=datetime(
                            2025, 1, 27, 18, 40, tzinfo=timezone.utc
                        ),
                        modified_by="PersonM",
                        reagents=[
                            SlimsReagentData(
                                name="112372-100G",
                                source=None,
                                lot_number="stbk5149",
                            )
                        ],
                    )
                ],
            )
        ]

        self.assertEqual(expected_output[0], output[0])

    def test_map_specimen_procedures(self):
        """Tests that specimen procedures are mapped correctly"""

        mapper = SlimsHistologyMapper(slims_hist_data=self.slims_hist_data)
        mapped_procedures = mapper.map_slims_info_to_specimen_procedures()
        mapped_procedures_json = [
            proc.model_dump_json() for proc in mapped_procedures
        ]
        mapped_procedures_json_parsed = [
            json.loads(json_str) for json_str in mapped_procedures_json
        ]
        self.assertEqual(len(mapped_procedures), 4)
        self.assertEqual(
            mapped_procedures_json_parsed, self.expected_procedures_json
        )

    def test_get_last_valid_end_time_edge_case(self):
        """Test returns None when no washes have end_time."""
        washes = [
            WashData(wash_type="Type1", end_time=None),
            WashData(wash_type="Type2", end_time=None),
            WashData(wash_type=None, end_time=None),
        ]
        result = self.mapper._get_last_valid_end_time(washes)
        self.assertIsNone(result)

    def test_map_slims_info_to_specimen_procedures_edge_case(self):
        """
        Tests that specimen procedures are not created unless
        a valid specimen procedure type is found."""
        slims_hist_data = SlimsHistologyData(
            procedure_name="Some Other Procedure"
        )
        mapper = SlimsHistologyMapper(slims_hist_data=[slims_hist_data])
        self.assertEqual(mapper.map_slims_info_to_specimen_procedures(), [])


if __name__ == "__main__":
    unittest.main()
