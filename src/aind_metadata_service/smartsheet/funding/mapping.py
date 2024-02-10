"""Module that handles the methods to map the SmartSheet response to the
aind-data-schema Funding model."""

import logging
from typing import List, Optional, Union

from aind_data_schema.core.data_description import Funding
from aind_data_schema.models.organizations import Organization
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.funding.models import FundingColumnNames
from aind_metadata_service.smartsheet.mapper import SmartSheetMapper
from aind_metadata_service.smartsheet.models import SheetRow


class FundingMapper(SmartSheetMapper):
    """Primary class to handle mapping data models and returning a response"""

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
        Union[Institution, str]
          Either an Institution parsed from the name. If the Institution can't
          be generated from the name, then it returns the input name.

        """
        if Organization().name_map.get(input_name) is not None:
            return Organization().name_map.get(input_name)
        else:
            try:
                return Organization.from_abbreviation(input_name)
            except KeyError:
                return input_name

    def _map_row_to_funding(
        self, row: SheetRow, input_project_name: str
    ) -> Optional[Funding]:
        """
        Map a row to an optional funding model.
        Parameters
        ----------
        row : SheetRow
        input_project_name : str
          The project name the user inputs

        Returns
        -------
        Union[Funding, None]
          None if the project name in the row doesn't match the
          input_project_name. Otherwise, will try to return a valid Funding
          model. If there is some data entry mistake, then it will return a
          Funding model as good as it can.

        """

        row_dict = self.map_row_to_dict(row)
        project_name = row_dict.get(FundingColumnNames.PROJECT_NAME)
        grant_number = row_dict.get(FundingColumnNames.GRANT_NUMBER)
        institution_value = row_dict.get(
            FundingColumnNames.FUNDING_INSTITUTION
        )
        funder = self._parse_institution(institution_value)
        investigators = row_dict.get(FundingColumnNames.INVESTIGATORS)
        if input_project_name != project_name:
            return None
        else:
            try:
                return Funding(
                    funder=funder,
                    grant_number=grant_number,
                    fundee=investigators,
                )
            except ValidationError:
                return Funding.model_construct(
                    funder=funder,
                    grant_number=grant_number,
                    fundee=investigators,
                )

    def _get_funding_list(self, project_name: str) -> List[Funding]:
        """
        Return a list of Funding information for a give project code.
        Parameters
        ----------
        project_name : str
          The project name that the user inputs.

        Returns
        -------
        List[Funding]
          A list of Funding models. They might not necessarily pass validation
          checks.
        """
        rows_associated_with_project_name: List[Funding] = []
        for row in self.model.rows:
            opt_funding: Optional[Funding] = self._map_row_to_funding(
                row=row, input_project_name=project_name
            )
            if opt_funding is not None:
                rows_associated_with_project_name.append(opt_funding)
        return rows_associated_with_project_name

    def _get_model_response(self) -> ModelResponse:
        """
        Return a ModelResponse
        Returns
        -------
        ModelResponse
          Will either be an internal server error response or a database
          responded response. Validation checks are performed downstream.

        """
        try:
            funding_list = self._get_funding_list(project_name=self.input_id)
            return ModelResponse(
                aind_models=funding_list, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()
