"""Module that handles the methods to map the FundingModel response to the
aind-data-schema Funding model."""

import logging
import re
from typing import List, Optional, Tuple

from aind_data_schema.components.identifiers import Person
from aind_data_schema.core.data_description import Funding
from aind_data_schema_models.organizations import Organization
from aind_smartsheet_service_async_client.models import FundingModel
from pydantic import ValidationError


class FundingMapper:
    """Class to handle mapping of funding data"""

    def __init__(self, smartsheet_funding: List[FundingModel]):
        """
        Class constructor
         Parameters
         ----------
         smartsheet_funding : List[FundingModel]
        """
        self.smartsheet_funding = smartsheet_funding

    @staticmethod
    def split_name(input_name: str) -> Tuple[str, Optional[str]]:
        """Splits name into project name and subproject name"""
        name_pattern = r"(.*) - (.*)"
        if not re.match(name_pattern, input_name):
            return input_name, None
        else:
            groups = re.match(name_pattern, input_name).groups()
            return groups[0], groups[1]

    @staticmethod
    def _parse_institution(
        input_name: Optional[str],
    ) -> List[Person]:
        """
        Generate Institution from string
        Parameters
        ----------
        input_name : Optional[str]
          Institution name

        Returns
        -------
        Union[Organization, str, None]
          Either an Organization parsed from the name or input.
        """
        if input_name is None:
            return None
        elif Organization().name_map.get(input_name) is not None:
            return Organization().name_map.get(input_name)
        elif Organization().abbreviation_map.get(input_name) is not None:
            return Organization().abbreviation_map.get(input_name)
        else:
            return input_name

    @staticmethod
    def _parse_person_names(
        input_names: Optional[str],
    ) -> Optional[List[Person]]:
        """
        Parse person names from a string.

        Parameters
        ----------
        input_names : Optional[str]
          Person names as a comma-separated string.

        Returns
        -------
        List[Person]
        List of parsed Person instances.
        """
        if input_names is None or input_names.strip() == "":
            return None

        names = [name.strip() for name in input_names.split(",")]
        persons = [Person(name=name) for name in names if name]
        return persons

    def _map_funding_to_funding_information(
        self,
        smartsheet_funding: FundingModel,
    ) -> Optional[Funding]:
        """
        Map a FundingModel to an optional Funding model.

        Parameters
        ----------
        smartsheet_funding : FundingModel
            Single funding model instance

        Returns
        -------
        Funding | None
            If no relevant funding information is found, then None.
            Otherwise, a Funding model with parsed data.
        """
        grant_number = smartsheet_funding.grant_number
        institution_value = smartsheet_funding.funding_institution
        funder = self._parse_institution(institution_value)
        fundees = self._parse_person_names(smartsheet_funding.fundees__pi)

        if funder is None and grant_number is None and fundees is None:
            return None

        try:
            return Funding(
                funder=funder,
                grant_number=grant_number,
                fundee=fundees,
            )
        except ValidationError as e:
            logging.warning(f"Validation error creating Funding model: {e}")
            return Funding.model_construct(
                funder=funder,
                grant_number=grant_number,
                fundee=fundees,
            )

    def get_funding_list(self) -> List[Funding]:
        """
        Return a list of Funding models for a given project name.

        Returns
        -------
        List[Funding]
            A list of Funding models.
        """
        funding_list: List[Funding] = []

        for smartsheet_funding in self.smartsheet_funding:
            funding_info = self._map_funding_to_funding_information(
                smartsheet_funding=smartsheet_funding,
            )
            if funding_info is not None:
                funding_list.append(funding_info)

        return funding_list

    def get_investigators_list(self) -> List[Person]:
        """
        Get list of investigators from funding data

        Returns
        -------
        List[Person]
            List of unique investigators
        """
        investigators_list: List[Person] = []
        for smartsheet_funding in self.smartsheet_funding:
            investigators = self._parse_person_names(
                smartsheet_funding.investigators
            )
            if investigators:
                investigators_list.extend(investigators)
        return investigators_list

    def get_project_names(self) -> List[str]:
        """
        Get list of project names from funding data

        Returns
        -------
        List[str]
            Sorted list of unique project names
        """
        project_names = set()

        for smartsheet_funding in self.smartsheet_funding:
            project_name = smartsheet_funding.project_name
            subproject_name = smartsheet_funding.subproject

            if project_name is not None and subproject_name is None:
                project_names.add(project_name)
            elif project_name is not None and subproject_name is not None:
                project_names.add(f"{project_name} - {subproject_name}")

        return sorted(list(project_names))
