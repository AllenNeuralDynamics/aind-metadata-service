"""Tests mapper module"""

import unittest

from aind_data_schema.core.data_description import Funding
from aind_data_schema_models.organizations import Organization

from aind_metadata_service.backends.smartsheet.models import FundingModel
from aind_metadata_service.routers.funding.mapper import Mapper


class TestMapper(unittest.TestCase):
    """Tests methods in Mapper class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up class with example data."""
        cls.mapper = Mapper(
            funding_model=FundingModel(
                project_name="AIND Scientific Activities",
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                investigators="person.two@acme.org, J Smith, John Doe II",
            )
        )

    def test_parse_institution_success(self):
        """Tests _parse_institution success"""
        actual_org = self.mapper._parse_institution("Allen Institute")
        expected_org = Organization.AI
        self.assertEqual(expected_org, actual_org)

    def test_parse_institution_abbreviation_success(self):
        """Tests _parse_institution success when abbreviation is used."""
        actual_org = self.mapper._parse_institution("AI")
        expected_org = Organization.AI
        self.assertEqual(expected_org, actual_org)

    def test_parse_institution_failure(self):
        """Tests _parse_institution failure. The expected behavior is to
        return the org name as a string."""
        actual_org = self.mapper._parse_institution("Nonesuch Org")
        self.assertEqual("Nonesuch Org", actual_org)

    def test_map_to_funding_valid(self):
        """Tests map to funding method when a valid model is returned"""
        mapped_model = self.mapper.map_to_funding()
        expected_model = Funding(
            funder=Organization.AI,
            fundee="person.two@acme.org, J Smith, John Doe II",
        )
        self.assertEqual(expected_model, mapped_model)

    def test_map_to_funding_invalid(self):
        """Tests map to funding method when an invalid model is returned"""
        mapper = Mapper(
            funding_model=FundingModel(
                project_name="AIND Scientific Activities",
                project_code="122-01-001-10",
                funding_institution="Misnamed organization here",
                investigators="person.two@acme.org, J Smith, John Doe II",
            )
        )
        mapped_model = mapper.map_to_funding()
        expected_model = Funding.model_construct(
            funder="Misnamed organization here",
            fundee="person.two@acme.org, J Smith, John Doe II",
        )
        self.assertEqual(expected_model, mapped_model)


if __name__ == "__main__":
    unittest.main()
