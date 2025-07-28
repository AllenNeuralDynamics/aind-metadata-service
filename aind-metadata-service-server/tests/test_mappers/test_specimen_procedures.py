"""Tests methods in mapping module"""

import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from aind_data_schema.core.procedures import SpecimenProcedureType
from aind_slims_service_async_client.models import (
    HistologyReagentData,
    HistologyWashData,
    SlimsHistologyData,
)

from aind_metadata_service_server.mappers.specimen_procedures import (
    SpecimenProcedureMapper,
)


class TestSpecimenProcedureMapper(unittest.TestCase):
    """Tests methods in SpecimenProcedureMapper class"""

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

    def test_parse_html(self):
        """Test parsing of HTML links."""
        mapper = SpecimenProcedureMapper([])
        html_input = (
            '<a href="https://example.com/protocol" '
            'target="_blank">Protocol Link</a>'
        )
        expected_output = "https://example.com/protocol"
        output = mapper._parse_html(html_input)
        self.assertEqual(expected_output, output)

        output_invalid = mapper._parse_html("<div>Invalid Link</div>")
        self.assertEqual(None, output_invalid)

        output_none = mapper._parse_html(None)
        self.assertIsNone(output_none)

        with patch(
            "xml.etree.ElementTree.fromstring",
            side_effect=Exception("mock error"),
        ):
            result = mapper._parse_html(
                '<a href="https://example.com/protocol">Protocol Link</a>'
            )
            self.assertIsNone(result)

    def test_map_slims_response_to_aind_specimen_procedures_edge_case(self):
        """Test unknown procedure type edge case."""
        slims_hist_data = [
            SlimsHistologyData(procedure_name="Some Other Procedure")
        ]
        mapper = SpecimenProcedureMapper(slims_hist_data)
        self.assertEqual(
            mapper.map_slims_response_to_aind_specimen_procedures(), []
        )

    def test_get_last_valid_end_time_edge_case(self):
        """Test returns None when no washes have end_time."""
        washes = [
            HistologyWashData(wash_type="Type1", end_time=None),
            HistologyWashData(wash_type="Type2", end_time=None),
            HistologyWashData(wash_type=None, end_time=None),
        ]
        mapper = SpecimenProcedureMapper([])
        result = mapper._get_last_valid_end_time(washes)
        self.assertIsNone(result)

    def test_map_immunolabeling_procedure(self):
        """Test mapping of immunolabeling procedures and antibodies."""
        washes = [
            HistologyWashData(
                wash_name="Primary Antibody Wash",
                wash_type=None,
                start_time=datetime.fromtimestamp(1738688400),
                end_time=datetime.fromtimestamp(1738781400),
                modified_by="PersonM",
                reagents=[],
                mass="10.2",
            ),
            HistologyWashData(
                wash_name="Secondary Antibody Wash",
                wash_type=None,
                start_time=datetime.fromtimestamp(1738688400),
                end_time=datetime.fromtimestamp(1738781400),
                modified_by="PersonM",
                reagents=[],
                mass=None,
            ),
        ]
        slims_hist_data = [
            SlimsHistologyData(
                procedure_name="SmartSPIM Labeling",
                protocol_id=None,
                protocol_name=None,
                washes=washes,
                subject_id="744742",
            )
        ]
        mapper = SpecimenProcedureMapper(slims_hist_data)
        procedures = mapper.map_slims_response_to_aind_specimen_procedures()
        self.assertEqual(len(procedures), 2)
        self.assertEqual(
            procedures[0].procedure_type, SpecimenProcedureType.IMMUNOLABELING
        )
        self.assertEqual(
            procedures[0].antibodies.immunolabel_class.name, "PRIMARY"
        )
        self.assertEqual(procedures[0].antibodies.mass, Decimal("10.2"))
        self.assertEqual(
            procedures[1].antibodies.immunolabel_class.name, "SECONDARY"
        )
        self.assertIsNone(procedures[1].antibodies.mass)

    def test_map_antibody(self):
        """Test antibody mapping for primary and secondary washes."""
        mapper = SpecimenProcedureMapper([])
        primary_wash = HistologyWashData(
            wash_name="Primary Antibody Wash",
            wash_type=None,
            start_time=None,
            end_time=None,
            modified_by=None,
            reagents=[],
            mass="5.0",
        )
        secondary_wash = HistologyWashData(
            wash_name="Secondary Antibody Wash",
            wash_type=None,
            start_time=None,
            end_time=None,
            modified_by=None,
            reagents=[],
            mass=None,
        )
        none_wash = HistologyWashData(
            wash_name="Unknown Wash",
            wash_type=None,
            start_time=None,
            end_time=None,
            modified_by=None,
            reagents=[],
            mass=None,
        )
        antibody_primary = mapper._map_antibody(primary_wash)
        antibody_secondary = mapper._map_antibody(secondary_wash)
        antibody_none = mapper._map_antibody(none_wash)
        self.assertEqual(antibody_primary.immunolabel_class.name, "PRIMARY")
        self.assertEqual(antibody_primary.mass, Decimal(5.0))
        self.assertEqual(
            antibody_secondary.immunolabel_class.name, "SECONDARY"
        )
        self.assertIsNone(antibody_secondary.mass)
        self.assertIsNone(antibody_none)

    def test_map_slims_response_to_aind_specimen_procedures(self):
        """Test mapping with all provided test data."""
        delipidation_washes = [
            HistologyWashData(
                wash_name="Wash 1",
                wash_type="Methanol Gradient",
                start_time=datetime.fromtimestamp(1738688400),
                end_time=datetime.fromtimestamp(1738710000),
                modified_by="PersonM",
                reagents=[
                    HistologyReagentData(
                        name="34860-1L-R", source=None, lot_number="SHBR4455"
                    )
                ],
                mass=None,
            ),
            HistologyWashData(
                wash_name="Wash 2",
                wash_type="Methanol + DCM",
                start_time=datetime.fromtimestamp(1738710000),
                end_time=datetime.fromtimestamp(1738781400),
                modified_by="PersonM",
                reagents=[
                    HistologyReagentData(
                        name="270997-1L", source=None, lot_number="SHBQ9167"
                    ),
                    HistologyReagentData(
                        name="34860-1L-R", source=None, lot_number="SHBR4455"
                    ),
                ],
                mass=None,
            ),
            HistologyWashData(
                wash_name="Wash 3",
                wash_type=None,
                start_time=None,
                end_time=None,
                modified_by="PersonM",
                reagents=[],
                mass=None,
            ),
        ]
        refractive_washes = [
            HistologyWashData(
                wash_name="Refractive Index Matching Wash",
                wash_type="Refractive Index Matching",
                start_time=datetime.fromtimestamp(1738784100),
                end_time=datetime.fromtimestamp(1738956900),
                modified_by="PersonM",
                reagents=[
                    HistologyReagentData(
                        name="112372-100G", source=None, lot_number="stbk5149"
                    )
                ],
                mass=None,
            )
        ]
        slims_hist_data = [
            SlimsHistologyData(
                procedure_name="SmartSPIM Delipidation",
                protocol_id=(
                    "https://www.protocols.io/edit/"
                    "refractive-index-matching-ethyl-cinnamate-cukpwuvn"
                ),
                protocol_name=(
                    "iDISCO: Dichloromethane Whole Mouse Brain Delipidation"
                ),
                washes=delipidation_washes,
                subject_id="744742",
            ),
            SlimsHistologyData(
                procedure_name="SmartSPIM Labeling",
                protocol_id=None,
                protocol_name=None,
                washes=[
                    HistologyWashData(
                        wash_name="Primary Antibody Wash",
                        wash_type=None,
                        start_time=datetime.fromtimestamp(1738688400),
                        end_time=datetime.fromtimestamp(1738781400),
                        modified_by="PersonM",
                        reagents=[],
                        mass="10.2",
                    ),
                    HistologyWashData(
                        wash_name="Secondary Antibody Wash",
                        wash_type=None,
                        start_time=datetime.fromtimestamp(1738688400),
                        end_time=datetime.fromtimestamp(1738781400),
                        modified_by="PersonM",
                        reagents=[],
                        mass=None,
                    ),
                ],
                subject_id="744742",
            ),
            SlimsHistologyData(
                procedure_name="SmartSPIM Refractive Index Matching",
                protocol_id=None,
                protocol_name=None,
                washes=refractive_washes,
                subject_id="744742",
            ),
        ]
        mapper = SpecimenProcedureMapper(slims_hist_data)
        procedures = mapper.map_slims_response_to_aind_specimen_procedures()
        self.assertEqual(len(procedures), 4)
        self.assertEqual(
            procedures[0].procedure_type, SpecimenProcedureType.DELIPIDATION
        )
        self.assertEqual(
            procedures[1].procedure_type, SpecimenProcedureType.IMMUNOLABELING
        )
        self.assertEqual(
            procedures[2].procedure_type, SpecimenProcedureType.IMMUNOLABELING
        )
        self.assertEqual(
            procedures[3].procedure_type,
            SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING,
        )


if __name__ == "__main__":
    unittest.main()
