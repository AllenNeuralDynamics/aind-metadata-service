"""Tests handler module"""

import json
import os
import unittest
import warnings
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

from aind_smartsheet_api.client import SmartsheetClient

from aind_metadata_service.backends.smartsheet.configs import (
    SmartsheetSettings,
)
from aind_metadata_service.backends.smartsheet.handler import SessionHandler
from aind_metadata_service.backends.smartsheet.models import (
    FundingModel,
    PerfusionsModel,
    ProtocolsModel,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
RESOURCE_DIR = TEST_DIR / "resources" / "backends" / "smartsheet"


class TestSessionHandler(unittest.TestCase):
    """Test methods in SessionHandler Class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class with loaded json and shared examples."""

        # TODO: There is deprecation warning coming from the
        #  smartsheet-python-sdk package. Once it's fixed there, we can
        #  upgrade and remove this filter.
        warnings.simplefilter("ignore", category=DeprecationWarning)

        with open(RESOURCE_DIR / "funding.json", "r") as f:
            funding_response = json.load(f)

        with open(RESOURCE_DIR / "perfusions.json", "r") as f:
            perfusions_response = json.load(f)

        with open(RESOURCE_DIR / "protocols.json", "r") as f:
            protocols_response = json.load(f)

        cls.funding_response = json.dumps(funding_response)
        cls.perfusions_response = json.dumps(perfusions_response)
        cls.protocols_response = json.dumps(protocols_response)

        cls.expected_funding_sheet = [
            FundingModel(
                project_name="AIND Scientific Activities",
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                investigators="person.two@acme.org, J Smith, John Doe II",
            ),
            FundingModel(
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                investigators="John Doe, person.one@acme.org",
            ),
            FundingModel(
                project_name="v1omFISH",
                project_code="121-01-010-10",
                funding_institution="Allen Institute",
                investigators="person.one@acme.org, Jane Doe",
            ),
        ]
        cls.expected_perfusions_sheet = [
            PerfusionsModel(
                subject_id=Decimal("689418.0"),
                date=date(2023, 10, 2),
                experimenter="Jane Smith",
                iacuc_protocol=(
                    "2109 - Analysis of brain "
                    "- wide neural circuits in the mouse"
                ),
                animal_weight_prior=Decimal("22.0"),
                output_specimen_id=Decimal("689418.0"),
                postfix_solution="1xPBS",
                notes="Good",
            )
        ]
        cls.expected_protocols_sheet = [
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Immunolabeling",
                protocol_name="Immunolabeling of a Whole Mouse Brain",
                doi="dx.doi.org/10.17504/protocols.io.ewov1okwylr2/v1",
                version=Decimal("1.0"),
            ),
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Tetrahydrofuran and Dichloromethane Delipidation of a "
                    "Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
                version=Decimal("1.0"),
            ),
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Aqueous (SBiP) Delipidation of a Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.n2bvj81mwgk5/v1",
                version=Decimal("1.0"),
            ),
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Gelation + previous steps",
                protocol_name=(
                    "Whole Mouse Brain Delipidation, Immunolabeling, and "
                    "Expansion Microscopy"
                ),
                doi="dx.doi.org/10.17504/protocols.io.n92ldpwjxl5b/v1",
                version=Decimal("1.0"),
                protocol_collection=False,
            ),
            ProtocolsModel(
                protocol_type="Surgical Procedures",
                procedure_name="Injection Nanoject",
                protocol_name="Injection of Viral Tracers by Nanoject V.4",
                doi="dx.doi.org/10.17504/protocols.io.bp2l6nr7kgqe/v4",
                version=Decimal("4.0"),
            ),
            ProtocolsModel(
                protocol_type="Surgical Procedures",
                procedure_name="Injection Iontophoresis",
                protocol_name=(
                    "Stereotaxic Surgery for Delivery of Tracers by "
                    "Iontophoresis V.3"
                ),
                doi="dx.doi.org/10.17504/protocols.io.bgpvjvn6",
                version=Decimal("3.0"),
            ),
            ProtocolsModel(
                protocol_type="Surgical Procedures",
                procedure_name="Perfusion",
                protocol_name=(
                    "Mouse Cardiac Perfusion Fixation and Brain "
                    "Collection V.5"
                ),
                doi="dx.doi.org/10.17504/protocols.io.bg5vjy66",
                version=Decimal("5.0"),
            ),
            ProtocolsModel(
                protocol_type="Imaging Techniques",
                procedure_name="SmartSPIM Imaging",
                protocol_name="Imaging cleared mouse brains on SmartSPIM",
                doi="dx.doi.org/10.17504/protocols.io.3byl4jo1rlo5/v1",
                version=Decimal("1.0"),
            ),
            ProtocolsModel(
                protocol_type="Imaging Techniques",
                procedure_name="SmartSPIM setup",
                protocol_name="SmartSPIM setup and alignment",
                doi="dx.doi.org/10.17504/protocols.io.5jyl8jyb7g2w/v1",
                version=Decimal("1.0"),
            ),
            ProtocolsModel(),
            ProtocolsModel(),
            ProtocolsModel(),
            ProtocolsModel(),
        ]

        test_client = SmartsheetClient(
            smartsheet_settings=SmartsheetSettings(access_token="abc-123")
        )
        cls.test_handler = SessionHandler(session=test_client)

    @patch("aind_smartsheet_api.client.SmartsheetClient.get_raw_sheet")
    def test_get_funding_sheet(self, mock_get_raw_sheet: MagicMock):
        """Tests get_parsed_sheet method for funding"""
        mock_get_raw_sheet.return_value = self.funding_response
        parsed_sheet = self.test_handler.get_parsed_sheet(
            sheet_id=2802362280267652, model=FundingModel
        )
        self.assertEqual(self.expected_funding_sheet, parsed_sheet)

    @patch("aind_smartsheet_api.client.SmartsheetClient.get_raw_sheet")
    def test_get_perfusions_sheet(self, mock_get_raw_sheet: MagicMock):
        """Tests get_parsed_sheet method for perfusions"""
        mock_get_raw_sheet.return_value = self.perfusions_response
        parsed_sheet = self.test_handler.get_parsed_sheet(
            sheet_id=6224804269956, model=PerfusionsModel
        )
        self.assertEqual(self.expected_perfusions_sheet, parsed_sheet)

    @patch("aind_smartsheet_api.client.SmartsheetClient.get_raw_sheet")
    def test_get_protocols_sheet(self, mock_get_raw_sheet: MagicMock):
        """Tests get_parsed_sheet method for protocols"""
        mock_get_raw_sheet.return_value = self.protocols_response
        parsed_sheet = self.test_handler.get_parsed_sheet(
            sheet_id=7478444220698500, model=ProtocolsModel
        )
        self.assertEqual(self.expected_protocols_sheet, parsed_sheet)

    def test_get_project_funding_info_match(self):
        """Tests get_project_funding_info match"""

        funding_info = self.test_handler.get_project_funding_info(
            self.expected_funding_sheet, project_name="v1omFISH"
        )
        self.assertEqual(self.expected_funding_sheet[2:3], funding_info)

    def test_get_project_funding_info_no_match(self):
        """Tests get_project_funding_info when no match"""

        funding_info = self.test_handler.get_project_funding_info(
            self.expected_funding_sheet, project_name="FAKE PROJECT"
        )
        self.assertEqual([], funding_info)

    def test_get_project_names(self):
        """Tests get_project_names"""

        project_names = self.test_handler.get_project_names(
            self.expected_funding_sheet,
        )
        expected_names = ["AIND Scientific Activities", "v1omFISH"]
        self.assertEqual(expected_names, project_names)

    def test_get_protocols_info_match(self):
        """Tests get_protocols_info match"""

        protocol_info = self.test_handler.get_protocols_info(
            self.expected_protocols_sheet,
            protocol_name="Immunolabeling of a Whole Mouse Brain",
        )
        self.assertEqual(self.expected_protocols_sheet[0:1], protocol_info)

    def test_get_protocols_info_no_match(self):
        """Tests get_protocols_info when no match"""

        protocol_info = self.test_handler.get_protocols_info(
            self.expected_protocols_sheet, protocol_name="FAKE PROTOCOL"
        )
        self.assertEqual([], protocol_info)

    def test_get_perfusions_info_match(self):
        """Tests get_perfusions_info match"""

        perfusions_info = self.test_handler.get_perfusions_info(
            self.expected_perfusions_sheet, subject_id="689418"
        )
        self.assertEqual(self.expected_perfusions_sheet[0:1], perfusions_info)

    def test_get_perfusions_info_no_match(self):
        """Tests get_perfusions_info when no match"""

        perfusions_info = self.test_handler.get_perfusions_info(
            self.expected_perfusions_sheet, subject_id="0"
        )
        self.assertEqual([], perfusions_info)


if __name__ == "__main__":
    unittest.main()
