"""Module to test SlimsHistologyMapper methods"""

import json
import os
import unittest
from pathlib import Path

from aind_data_schema.core.procedures import SpecimenProcedureType
from aind_slims_api.models.experiment_run_step import SlimsWashRunStep
from aind_slims_api.operations.histology_procedures import (
    SlimsWash,
    SPIMHistologyExpBlock,
)

from aind_metadata_service.slims.procedures.mapping import SlimsHistologyMapper
from aind_metadata_service.slims.procedures.models import (
    SlimsExperimentTemplateNames,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
)
RAW_DIR = RESOURCES_DIR / "raw"
MAPPED_DIR = RESOURCES_DIR / "mapped"


class TestSlimsHistologyMapper(unittest.TestCase):
    """Class to test methods of SlimsHistologyMapper"""

    def setUp(self):
        """Set up test class"""
        self.mapper = SlimsHistologyMapper()
        with open(RAW_DIR / "histology_procedures_response.json") as f:
            slims_data1 = json.load(f)
        with open(MAPPED_DIR / "specimen_procedures.json") as f:
            expected_data1 = json.load(f)
        with open(RAW_DIR / "histology_procedures_response2.json") as f:
            slims_data2 = json.load(f)
        with open(MAPPED_DIR / "specimen_procedures2.json") as f:
            expected_data2 = json.load(f)
        self.blocks1 = [
            SPIMHistologyExpBlock.model_validate(block)
            for block in slims_data1
        ]
        self.blocks2 = [
            SPIMHistologyExpBlock.model_validate(block)
            for block in slims_data2
        ]
        self.expected_procedures = [expected_data1, expected_data2]

    def test_map_procedure_type(self):
        """Tests that immunolabeling procedure type is mapped correctly"""
        block_name = SlimsExperimentTemplateNames.SMARTSPIM_LABELING
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertEqual(procedure_type, SpecimenProcedureType.IMMUNOLABELING)

        block_name = SlimsExperimentTemplateNames.EXASPIM_LABELING
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertEqual(procedure_type, SpecimenProcedureType.IMMUNOLABELING)

        block_name = SlimsExperimentTemplateNames.SMARTSPIM_DELIPIDATION
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertEqual(procedure_type, SpecimenProcedureType.DELIPIDATION)

        block_name = SlimsExperimentTemplateNames.EXASPIM_DELIPIDATION
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertEqual(procedure_type, SpecimenProcedureType.DELIPIDATION)

        block_name = SlimsExperimentTemplateNames.SMARTSPIM_RI_MATCHING
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertEqual(
            procedure_type, SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING
        )

        block_name = SlimsExperimentTemplateNames.EXASPIM_GELATION
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertEqual(procedure_type, SpecimenProcedureType.GELATION)

        block_name = SlimsExperimentTemplateNames.EXASPIM_EXPANSION
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertEqual(procedure_type, SpecimenProcedureType.EXPANSION)

        block_name = "UNKNOWN_TEMPLATE"
        procedure_type = self.mapper._map_procedure_type(block_name)
        self.assertIsNone(procedure_type)

    def test_map_experimenters(self):
        """Tests experimenters list is mapped as expected"""
        wash1 = SlimsWash.model_construct(
            wash_step=SlimsWashRunStep(modified_by="experimenter1")
        )
        wash2 = SlimsWash.model_construct(
            wash_step=SlimsWashRunStep(modified_by="experimenter2")
        )
        experimenters = self.mapper._map_experimenters(
            washes=[wash1, wash2, wash1]
        )
        self.assertEqual(len(experimenters), 2)

    def test_map_antibody_edge_case(self):
        """Tests map antibody edge cases"""
        wash = SlimsWash.model_construct()
        self.assertIsNone(self.mapper._map_antibody(wash))
        wash2 = SlimsWash.model_construct(wash_step="some wash step")
        self.assertIsNone(self.mapper._map_antibody(wash2))

    def test_map_specimen_procedures(self):
        """Tests that specimen procedures are mapped correctly"""
        specimen_id = "000000"
        specimen_procedures = self.mapper.map_specimen_procedures(
            self.blocks1, specimen_id
        )
        self.assertEqual(len(specimen_procedures), 4)
        for i, procedure in enumerate(specimen_procedures):
            self.assertEqual(
                json.loads(procedure.model_dump_json()),
                self.expected_procedures[0][i],
            )

        specimen_procedures = self.mapper.map_specimen_procedures(
            self.blocks2, specimen_id
        )
        self.assertEqual(len(specimen_procedures), 2)
        for i, procedure in enumerate(specimen_procedures):
            self.assertEqual(
                json.loads(procedure.model_dump_json()),
                self.expected_procedures[1][i],
            )


if __name__ == "__main__":
    unittest.main()
