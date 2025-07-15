"""Module that handles the methods to map the FundingModel response to the
aind-data-schema Funding model."""

import logging
from typing import List, Optional, Union

from aind_data_schema_models.organizations import Organization
from pydantic import ValidationError
from aind_smartsheet_service_async_client.models import FundingModel
from aind_metadata_service_server.models import FundingInformation

class FundingMapper:
    """Primary class to handle mapping FundingModel to FundingInformation models"""

    def __init__(self, funding_data: List[FundingModel]):
        """
        Initialize mapper with list of FundingModel instances

        Parameters
        ----------
        funding_data : List[FundingModel]
            List of funding models from the service
        """
        self.funding_data = funding_data

    @staticmethod
    def _parse_institution(
        input_name: Optional[str],
    ) -> Optional[Union[Organization, str]]:
        """
        Generate Institution from string
        Parameters
        ----------
        input_name : Optional[str]
          Institution name

        Returns
        -------
        Optional[Union[Organization, str]]
          Either an Organization parsed from the name. If the Organization can't
          be generated from the name, then it returns the input name.
        """
        if input_name is None:
            return None
        elif Organization().name_map.get(input_name) is not None:
            return Organization().name_map.get(input_name)
        elif Organization().abbreviation_map.get(input_name) is not None:
            return Organization().abbreviation_map.get(input_name)
        else:
            return input_name

    def _map_funding_to_funding_information(
        self, smartsheet_funding: FundingModel,
    ) -> Optional[FundingInformation]:
        """
        Map a FundingModel to an optional FundingInformation model.

        Parameters
        ----------
        smartsheet_funding : FundingModel
            Single funding model instance

        Returns
        -------
        Optional[FundingInformation]
            None if no relevant funding information is found,
            otherwise a FundingInformation model with parsed data.
        """
        grant_number = smartsheet_funding.grant_number
        institution_value = smartsheet_funding.funding_institution
        funder = self._parse_institution(institution_value)
        investigators = smartsheet_funding.investigators
        fundees = smartsheet_funding.fundees

        if (
            funder is None
            and grant_number is None
            and investigators is None
            and fundees is None
        ):
            return None

        try:
            return FundingInformation(
                funder=funder,
                grant_number=grant_number,
                fundee=fundees,
                investigators=investigators,
            )
        except ValidationError as e:
            logging.warning(f"Validation error creating FundingInformation model: {e}")
            return FundingInformation.model_construct(
                funder=funder,
                grant_number=grant_number,
                fundee=fundees,
                investigators=investigators,
            )

    def get_funding_list(self) -> List[FundingInformation]:
        """
        Return a list of FundingInformation models for a given project name.

        Parameters
        ----------
        project_name : str
            The project name that the user inputs.

        Returns
        -------
        List[FundingInformation]
            A list of FundingInformation models.
        """
        funding_list: List[FundingInformation] = []

        for smartsheet_funding in self.funding_data:
            funding_info = self._map_funding_to_funding_information(
                smartsheet_funding=smartsheet_funding,
            )
            if funding_info is not None:
                funding_list.append(funding_info)

        return funding_list

    def get_project_names(self) -> List[str]:
        """
        Get list of project names from funding data

        Returns
        -------
        List[str]
            Sorted list of unique project names
        """
        project_names = set()

        for smartsheet_funding in self.funding_data:
            project_name = smartsheet_funding.project_name
            subproject_name = smartsheet_funding.subproject

            if project_name is not None and subproject_name is None:
                project_names.add(project_name)
            elif project_name is not None and subproject_name is not None:
                project_names.add(f"{project_name} - {subproject_name}")

        return sorted(list(project_names))