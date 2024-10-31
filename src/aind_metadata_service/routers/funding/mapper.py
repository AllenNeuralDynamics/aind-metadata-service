"""Module to handle mapping Smartsheet funding model to AIND Funding model"""

from typing import Union

from aind_data_schema.core.data_description import Funding
from aind_data_schema_models.organizations import Organization
from pydantic import ValidationError

from aind_metadata_service.backends.smartsheet.models import FundingModel


class Mapper:
    """Class to handle mapping data into Funding model."""

    def __init__(self, funding_model: FundingModel):
        """Class constructor."""
        self.funding_model = funding_model

    @staticmethod
    def _parse_institution(input_name: str) -> Union[Organization, str]:
        """
        Generate Institution from string
        Parameters
        ----------
        input_name : str
          Institution name

        Returns
        -------
        Organization | str
          Either an Institution parsed from the name. If the Institution can't
          be generated from the name, then it returns the input name.

        """
        if Organization().name_map.get(input_name) is not None:
            return Organization().name_map.get(input_name)
        elif Organization().abbreviation_map.get(input_name) is not None:
            return Organization().abbreviation_map.get(input_name)
        else:
            return input_name

    def map_to_funding(self) -> Funding:
        """Maps FundingModel to Funding"""
        funder = self._parse_institution(
            self.funding_model.funding_institution
        )
        try:
            return Funding(
                funder=funder,
                grant_number=self.funding_model.grant_number,
                fundee=self.funding_model.investigators,
            )
        except ValidationError:
            return Funding.model_construct(
                funder=funder,
                grant_number=self.funding_model.grant_number,
                fundee=self.funding_model.investigators,
            )
