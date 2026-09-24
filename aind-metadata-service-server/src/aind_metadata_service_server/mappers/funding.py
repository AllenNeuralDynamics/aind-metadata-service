"""Module that handles the methods to map the FundingModel response to the
aind-data-schema Funding model."""

import logging
from typing import Dict, List, Optional, Set, Union

from aind_data_schema.components.identifiers import Person
from aind_data_schema.core.data_description import Funding
from aind_data_schema_models.organizations import Organization
from aind_dataverse_service_async_client.models import FundingModel
from pydantic import ValidationError


class FundingMapper:
    """Class to handle mapping of funding data"""

    def __init__(self, dataverse_funding: List[FundingModel]):
        """
        Class constructor
         Parameters
         ----------
         dataverse_funding : List[FundingModel]
        """
        self.dataverse_funding = dataverse_funding

    @staticmethod
    def _parse_institution(
        input_name: Optional[str],
    ) -> Union[Organization, str, None]:
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

    def _map_funding_to_funding_information(
        self,
        institution: Optional[str],
        grant_number: Optional[str],
        people_names: Set[str],
        people_map: Dict[str, Person],
    ) -> Optional[Funding]:
        """
        Map a FundingModel to an optional FundingInformation model.
        """
        funder = self._parse_institution(institution)
        fundees = [people_map.get(p) for p in people_names]
        fundees.sort(key=lambda p: p.name)
        if funder is None and grant_number is None and not fundees:
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

    def get_funding_list(
        self, project_name: str, resolved_people: List[Person]
    ) -> List[Funding]:
        """
        Return a list of Funding models for a given project name.

        Returns
        -------
        List[Funding]
            A list of Funding models.
        """
        people_map = {p.name: p for p in resolved_people}

        mapped_info = dict()
        for dataverse_funding in self.dataverse_funding:
            if dataverse_funding.project_name == project_name:
                key = (
                    dataverse_funding.funding_institution,
                    dataverse_funding.grant_number,
                )
                if mapped_info.get(key) is None:
                    mapped_info[key] = {
                        "people_names": set(),
                    }
                if dataverse_funding.fundees:
                    mapped_info[key]["people_names"].add(
                        dataverse_funding.fundees
                    )
                if dataverse_funding.investigators:
                    mapped_info[key]["people_names"].add(
                        dataverse_funding.investigators
                    )
        funding_info = []
        for k, v in mapped_info.items():
            parsed_info = self._map_funding_to_funding_information(
                institution=k[0],
                grant_number=k[1],
                people_names=v["people_names"],
                people_map=people_map,
            )
            if parsed_info is not None:
                funding_info.append(parsed_info)
        return funding_info

    def get_people_list(self, project_name: str) -> List[Person]:
        """
        Return a list of people for a given project name.

        Returns
        -------
        List[Person]
            A list of Person models.
        """

        people_names = set()
        for dataverse_funding in self.dataverse_funding:
            if dataverse_funding.project_name == project_name:
                fundees = dataverse_funding.fundees
                investigators = dataverse_funding.investigators
                if fundees is not None:
                    people_names.add(fundees)
                if investigators is not None:
                    people_names.add(investigators)
        people_list = [Person(name=p) for p in people_names]
        people_list.sort(key=lambda p: p.name)
        return people_list

    def get_investigators_list(self, project_name: str) -> List[Person]:
        """
        Get list of investigators from funding data

        Returns
        -------
        List[Person]
            List of unique investigators
        """
        investigators_set = set()
        for dataverse_funding in self.dataverse_funding:
            investigators = dataverse_funding.investigators
            if (
                dataverse_funding.project_name == project_name
                and dataverse_funding.investigators is not None
            ):
                investigators_set.add(investigators)
        investigators_list = [Person(name=p) for p in investigators_set]
        investigators_list.sort(key=lambda p: p.name)
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

        for dataverse_funding in self.dataverse_funding:
            project_name = dataverse_funding.project_name

            if project_name is not None:
                project_names.add(project_name)

        return sorted(list(project_names))
