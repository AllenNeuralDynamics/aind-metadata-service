"""Module to test FundingMapper class"""

import unittest
from pathlib import Path
import os
import json
from aind_data_schema.components.identifiers import Person
from aind_data_schema.core.data_description import Funding
from aind_data_schema_models.organizations import Organization
from aind_dataverse_service_async_client.models import FundingModel

from aind_metadata_service_server.mappers.funding import FundingMapper


RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "dataverse"
)


class TestFundingMapper(unittest.TestCase):
    """Class to test methods for FundingMapper."""

    def setUp(self):
        """Set up test data."""

        with open(RESOURCES_DIR / "funding_response.json") as f:
            funding_json = json.load(f)
        funding_models = [FundingModel.model_validate(r) for r in funding_json]
        self.mapper = FundingMapper(dataverse_funding=funding_models)
        self.resolved_people_project_1 = [
            Person(name="Person A", registry_identifier="1"),
            Person(name="Person X", registry_identifier="2"),
            Person(name="Person T"),
        ]


    def test_get_funding_list(self):
        """Tests get_funding_list method."""
        actual_funding = self.mapper.get_funding_list(
            project_name="PROJECT1",
            resolved_people=self.resolved_people_project_1
        )
        expected_funding = [
            Funding(
                funder=Organization.NINDS,
                grant_number="A1",
                fundee=[
            Person(name="Person A", registry_identifier="1"),
            Person(name="Person T"),
            Person(name="Person X", registry_identifier="2"),
        ],
            ),
            Funding(
                funder=Organization.NINDS,
                grant_number="B2",
                fundee=[
            Person(name="Person A", registry_identifier="1"),
            Person(name="Person T"),
            Person(name="Person X", registry_identifier="2"),
        ],
            ),
            Funding(
                funder=Organization.AI,
                grant_number=None,
                fundee=[Person(name="Person T"),]
            ),
        ]
        self.assertEqual(expected_funding, actual_funding)


    def test_mapping_empty_list(self):
        """Tests mapping with empty funding data list"""
        mapper = FundingMapper(dataverse_funding=[])
        funding_information = mapper.get_funding_list(
            project_name="A", resolved_people=[]
        )

        self.assertEqual([], funding_information)

    def test_mapping_all_empty(self):
        """Tests situation where all the info from the data source is None"""
        funding_model_invalid = FundingModel(
            project_name="Ephys Platform",
            subproject=None,
            funding_institution=None,
            grant_number=None,
            fundees=None,
            investigators=None,
        )

        dataverse_funding = [funding_model_invalid]
        mapper = FundingMapper(dataverse_funding=dataverse_funding)
        funding_information = mapper.get_funding_list(
            project_name="Ephys Platform", resolved_people=[]
        )
        self.assertEqual(0, len(funding_information))

    def test_mapping_invalid_institution(self):
        """Tests situation where the institute name isn't in
        aind-data-schema"""
        funding_model_invalid = FundingModel(
            project_name="Ephys Platform",
            subproject=None,
            funding_institution="Some Institute",
            grant_number=None,
            fundees="Person A",
            investigators="Person B",
        )
        resolved_people=[
            Person(name="Person A", registry_identifier="1"),
            Person(name="Person B", registry_identifier="2"),
        ]

        dataverse_funding = [funding_model_invalid]
        mapper = FundingMapper(dataverse_funding=dataverse_funding)
        with self.assertLogs(level="WARNING") as captured:
            funding_information = mapper.get_funding_list(
                project_name="Ephys Platform", resolved_people=resolved_people
            )
        self.assertEqual(1, len(captured.output))
        self.assertIn(
            "Validation error creating Funding model", captured.output[0]
        )

        expected_model = Funding.model_construct(
            funder="Some Institute",
            grant_number=None,
            fundee=resolved_people,
        )

        self.assertEqual(1, len(funding_information))
        self.assertEqual(expected_model.funder, funding_information[0].funder)
        self.assertEqual(
            expected_model.fundee[0].name,
            funding_information[0].fundee[0].name,
        )

    def test_get_project_names_success(self):
        """Tests successful retrieval of project names"""
        project_names = self.mapper.get_project_names()
        expected_names = ["PROJECT1", "PROJECT2-SUB_G"]
        self.assertEqual(sorted(expected_names), project_names)


    def test_get_project_names_empty(self):
        """Tests project names with empty data"""
        mapper = FundingMapper(dataverse_funding=[])
        project_names = mapper.get_project_names()
        self.assertEqual([], project_names)

    def test_parse_institution_valid(self):
        """Tests _parse_institution with valid organization name"""
        result = FundingMapper._parse_institution("Allen Institute")
        self.assertEqual(Organization.AI, result)

    def test_parse_institution_abbreviation(self):
        """Tests _parse_institution with organization abbreviation"""
        result = FundingMapper._parse_institution("NIMH")
        self.assertEqual(Organization.NIMH, result)

    def test_parse_institution_invalid(self):
        """Tests _parse_institution with invalid organization name"""
        result = FundingMapper._parse_institution("Some Random Institute")
        self.assertEqual("Some Random Institute", result)

    def test_parse_institution_none(self):
        """Tests _parse_institution with None input"""
        result = FundingMapper._parse_institution(None)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
