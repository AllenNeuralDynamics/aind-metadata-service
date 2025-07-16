"""Module to test FundingMapper class"""

import unittest

from aind_data_schema_models.organizations import Organization
from aind_smartsheet_service_async_client.models import FundingModel

from aind_metadata_service_server.mappers.funding import FundingMapper
from aind_metadata_service_server.models import FundingInformation


class TestFundingMapper(unittest.TestCase):
    """Class to test methods for FundingMapper."""

    def setUp(self):
        """Set up test data."""
        discovery_project = (
            "Discovery-Neuromodulator circuit dynamics during foraging"
        )
        sub1 = (
            "Subproject 1 Electrophysiological Recordings from NM Neurons"
            " During Behavior"
        )
        sub2 = "Subproject 2 Molecular Anatomy Cell Types"

        self.funding_sheet = [
            FundingModel(),
            FundingModel(
                project_name="Ephys Platform",
                funding_institution="Allen Institute",
                fundees="Person One, Person Two, Person Three",
            ),
            FundingModel(
                project_name="MSMA Platform",
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees="Person Four",
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-012-20",
                funding_institution="NINDS",
                grant_number="1RF1NS131984",
                fundees="Person Five, Person Six, Person Eight",
                investigators="Person Six, Person Eight",
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub2,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                fundees=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
                investigators="Person Seven",
            ),
        ]

    def test_mapping_success(self):
        """Tests successful mapping of funding data"""
        discovery_funding_rows = self.funding_sheet[3:5]
        mapper = FundingMapper(smartsheet_funding=discovery_funding_rows)
        funding_information = mapper.get_funding_list()
        expected_funding = [
            FundingInformation(
                funder=Organization.AI,
                grant_number=None,
                fundee=(
                    "Person Four, Person Five, Person Six,"
                    " Person Seven, Person Eight"
                ),
                investigators=None,
            ),
            FundingInformation(
                funder=Organization.NINDS,
                grant_number="1RF1NS131984",
                fundee="Person Five, Person Six, Person Eight",
                investigators="Person Six, Person Eight",
            ),
        ]
        self.assertEqual(len(funding_information), 2)
        self.assertEqual(funding_information, expected_funding)

    def test_mapping_empty_list(self):
        """Tests mapping with empty funding data list"""
        mapper = FundingMapper(smartsheet_funding=[])
        funding_information = mapper.get_funding_list()

        self.assertEqual([], funding_information)

    def test_mapping_empty_funding_model(self):
        """Tests mapping when funding model has all None fields"""
        empty_funding_row = [self.funding_sheet[0]]
        mapper = FundingMapper(smartsheet_funding=empty_funding_row)
        funding_information = mapper.get_funding_list()
        self.assertEqual([], funding_information)

    def test_mapping_invalid_institution(self):
        """Tests situation where the institute name isn't in
        aind-data-schema"""
        funding_model_invalid = FundingModel(
            project_name="Ephys Platform",
            subproject=None,
            funding_institution="Some Institute",
            grant_number=None,
            fundees="Person One, Person Two, Person Three",
            investigators=None,
        )

        smartsheet_funding = [funding_model_invalid]
        mapper = FundingMapper(smartsheet_funding=smartsheet_funding)
        funding_information = mapper.get_funding_list()

        expected_model = FundingInformation.model_construct(
            funder="Some Institute",
            grant_number=None,
            fundee="Person One, Person Two, Person Three",
            investigators=None,
        )

        self.assertEqual(1, len(funding_information))
        self.assertEqual(expected_model.funder, funding_information[0].funder)
        self.assertEqual(expected_model.fundee, funding_information[0].fundee)

    def test_get_project_names_success(self):
        """Tests successful retrieval of project names"""
        smartsheet_funding = [
            self.funding_sheet[3],
            self.funding_sheet[1],
            FundingModel(
                project_name=(
                    "Discovery-Neuromodulator circuit dynamics during foraging"
                ),
                subproject="Subproject 1 Electrophysiological Recordings",
                funding_institution="Allen Institute",
                grant_number=None,
                fundees=None,
                investigators=None,
            ),
        ]

        mapper = FundingMapper(smartsheet_funding=smartsheet_funding)
        project_names = mapper.get_project_names()

        expected_names = [
            "Discovery-Neuromodulator circuit dynamics during foraging - "
            "Subproject 1 Electrophysiological Recordings",
            "Discovery-Neuromodulator circuit dynamics during foraging - "
            "Subproject 1 Electrophysiological Recordings from NM Neurons "
            "During Behavior",
            "Ephys Platform",
        ]

        self.assertEqual(sorted(expected_names), project_names)

    def test_get_project_names_empty(self):
        """Tests project names with empty data"""
        mapper = FundingMapper(smartsheet_funding=[])
        project_names = mapper.get_project_names()

        self.assertEqual([], project_names)

    def test_get_project_names_with_none_values(self):
        """Tests project names when some projects have None values"""
        smartsheet_funding = [
            self.funding_sheet[1],
            self.funding_sheet[0],
        ]

        mapper = FundingMapper(smartsheet_funding=smartsheet_funding)
        project_names = mapper.get_project_names()

        expected_names = ["Ephys Platform"]
        self.assertEqual(expected_names, project_names)

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
