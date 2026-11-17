"""Tests methods in mapping module"""

import json
import unittest
from datetime import date
from pathlib import Path

from aind_data_schema.core.procedures import SpecimenProcedureType
from aind_dataverse_service_async_client.models import (
    HistologyModel,
    HistologyWashModel,
)

from aind_metadata_service_server.mappers.specimen_procedures import (
    SpecimenProcedureMapper,
)

EXAMPLE_HISTOLOGY_JSON = (
    Path(__file__).parent
    / ".."
    / "resources"
    / "dataverse"
    / "histology_response.json"
)


class TestSpecimenProcedureMapper(unittest.TestCase):
    """Tests methods in SpecimenProcedureMapper class"""

    @classmethod
    def setUpClass(cls):
        """Load example dataverse histology response"""
        with open(EXAMPLE_HISTOLOGY_JSON, "r") as f:
            contents = json.load(f)
        cls.histology = [HistologyModel.model_validate(r) for r in contents]

    def test_parse_specimen_procedure_name(self):
        """Test mapping of procedure_name to procedure_type."""
        mapper = SpecimenProcedureMapper([])
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
            output = mapper._parse_specimen_procedure_name(procedure_name=name)
            outputs.append(output)
        self.assertEqual(expected_types, outputs)

    def test_map_dataverse_response_edge_case(self):
        """Test unknown procedure type edge case."""
        mapper = SpecimenProcedureMapper(
            [HistologyModel(procedure_name="Some Other Procedure")]
        )
        self.assertEqual(
            mapper.map_dataverse_response_to_aind_specimen_procedures(), []
        )

    def test_map_dataverse_response_missing_fields(self):
        """Test missing specimen_id and washes are left empty."""
        mapper = SpecimenProcedureMapper(
            [
                HistologyModel(
                    procedure_name="SmartSPIM Delipidation",
                    subject_id="744742",
                ),
                HistologyModel(
                    procedure_name="SmartSPIM Labeling",
                    subject_id="744742",
                ),
            ]
        )
        procedures = (
            mapper.map_dataverse_response_to_aind_specimen_procedures()
        )
        self.assertEqual(1, len(procedures))
        self.assertIsNone(procedures[0].specimen_id)
        self.assertIsNone(procedures[0].start_date)
        self.assertIsNone(procedures[0].experimenter_full_name)
        self.assertEqual([], procedures[0].reagents)

    def test_get_last_valid_end_time_edge_case(self):
        """Test returns None when no washes have end_time."""
        washes = [
            HistologyWashModel(wash_type="Type1", end_time=None),
            HistologyWashModel(wash_type="Type2", end_time=None),
            HistologyWashModel(wash_type=None, end_time=None),
        ]
        mapper = SpecimenProcedureMapper([])
        result = mapper._get_last_valid_end_time(washes)
        self.assertIsNone(result)

    def test_map_antibody(self):
        """Test antibody mapping for primary and secondary washes."""
        mapper = SpecimenProcedureMapper([])
        antibody_primary = mapper._map_antibody(
            HistologyWashModel(wash_name="Primary Antibody Wash")
        )
        antibody_secondary = mapper._map_antibody(
            HistologyWashModel(wash_name="Secondary Antibody Wash")
        )
        antibody_none = mapper._map_antibody(
            HistologyWashModel(wash_name="Unknown Wash")
        )
        self.assertEqual(antibody_primary.immunolabel_class.name, "PRIMARY")
        self.assertIsNone(antibody_primary.mass)
        self.assertEqual(
            antibody_secondary.immunolabel_class.name, "SECONDARY"
        )
        self.assertIsNone(antibody_secondary.mass)
        self.assertIsNone(antibody_none)

    def test_map_dataverse_response_to_aind_specimen_procedures(self):
        """Test mapping with all provided test data."""
        mapper = SpecimenProcedureMapper(self.histology)
        procedures = (
            mapper.map_dataverse_response_to_aind_specimen_procedures()
        )
        self.assertEqual(
            [
                SpecimenProcedureType.DELIPIDATION,
                SpecimenProcedureType.IMMUNOLABELING,
                SpecimenProcedureType.IMMUNOLABELING,
                SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING,
            ],
            [p.procedure_type for p in procedures],
        )
        delipidation = procedures[0]
        self.assertEqual("744742-01", delipidation.specimen_id)
        self.assertEqual(
            "https://www.protocols.io/edit/"
            "refractive-index-matching-ethyl-cinnamate-cukpwuvn",
            delipidation.protocol_id,
        )
        self.assertEqual(
            "iDISCO: Dichloromethane Whole Mouse Brain Delipidation",
            delipidation.procedure_name,
        )
        self.assertEqual("PersonM", delipidation.experimenter_full_name)
        self.assertEqual(date(2025, 2, 4), delipidation.start_date)
        self.assertEqual(date(2025, 2, 5), delipidation.end_date)
        self.assertEqual(3, len(delipidation.reagents))
        self.assertEqual(
            "PRIMARY", procedures[1].antibodies.immunolabel_class.name
        )
        self.assertEqual(
            "SECONDARY", procedures[2].antibodies.immunolabel_class.name
        )
        self.assertEqual(
            "SmartSPIM Refractive Index Matching",
            procedures[3].procedure_name,
        )


if __name__ == "__main__":
    unittest.main()
