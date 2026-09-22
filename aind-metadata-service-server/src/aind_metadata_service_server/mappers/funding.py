"""Module that handles the methods to map the FundingModel response to the
aind-data-schema Funding model."""

import logging
from typing import List, Optional, Set, Union

from aind_data_schema_models.organizations import Organization
from aind_dataverse_service_async_client.models import FundingModel
from pydantic import ValidationError

from aind_metadata_service_server.models import FundingInformation


class FundingMapper:
    """Class to handle mapping of funding data"""

    def __init__(
        self,
        dataverse_funding: List[FundingModel],
    ):
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
        fundees: Set[str],
        investigators: Set[str],
    ) -> Optional[FundingInformation]:
        """
        Map a FundingModel to an optional FundingInformation model.
        """
        funder = self._parse_institution(institution)
        fundees_repr = (
            None if not fundees else ", ".join(sorted(list(fundees)))
        )
        investigators_repr = (
            None
            if not investigators
            else ", ".join(sorted(list(investigators)))
        )
        if (
            funder is None
            and grant_number is None
            and investigators_repr is None
            and fundees_repr is None
        ):
            return None

        try:
            return FundingInformation(
                funder=funder,
                grant_number=grant_number,
                fundee=fundees_repr,
                investigators=investigators_repr,
            )
        except ValidationError as e:
            logging.warning(
                f"Validation error creating FundingInformation model: {e}"
            )
            return FundingInformation.model_construct(
                funder=funder,
                grant_number=grant_number,
                fundee=fundees_repr,
                investigators=investigators_repr,
            )

    def get_funding_list(self, project_name: str) -> List[FundingInformation]:
        """
        Return a list of FundingInformation models for a given project name.

        Returns
        -------
        List[FundingInformation]
            A list of FundingInformation models.
        """

        mapped_info = dict()
        for dataverse_funding in self.dataverse_funding:
            if dataverse_funding.project_name == project_name:
                key = (
                    dataverse_funding.funding_institution,
                    dataverse_funding.grant_number,
                )
                if mapped_info.get(key) is None:
                    mapped_info[key] = {
                        "fundees": set(),
                        "investigators": set(),
                    }
                if dataverse_funding.fundees:
                    mapped_info[key]["fundees"].add(dataverse_funding.fundees)
                if dataverse_funding.investigators:
                    mapped_info[key]["investigators"].add(
                        dataverse_funding.investigators
                    )
        funding_info = []
        for k, v in mapped_info.items():
            parsed_info = self._map_funding_to_funding_information(
                institution=k[0],
                grant_number=k[1],
                fundees=v["fundees"],
                investigators=v["investigators"],
            )
            if parsed_info is not None:
                funding_info.append(parsed_info)
        return funding_info

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
